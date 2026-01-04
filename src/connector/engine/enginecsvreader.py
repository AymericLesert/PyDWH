# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the engine for reading csv files.
"""

from connector.engine.enginecsv import DWHConnectorDatabaseEngineCSV
from connector.database.record import DWHConnectorDatabaseRecord

class DWHConnectorDatabaseEngineCSVReader(DWHConnectorDatabaseEngineCSV):
    """This class defines a reading csv engine"""

    @property
    def handles(self):
        return self.__handles

    def open(self):
        """Open the CSV Files for read"""
        super().open()
        self.info("Openning the CSV files for read")
        self.__handles = {}
        for name in self.files:
            self.info(f"Openning the file '{name}' for read ...")
            try:
                self.__handles[name] = self.get_file(name, DWHConnectorDatabaseEngineCSV.CSVRead)
            except StopIteration:
                self.info("File empty")
            except:
                self.exception("Unable to open file")

    def get_tables(self):
        return [] if self.__handles is None else [name for name in self.__handles]

    def get_table(self, name, description):
        table = super().get_table(name, description)
        if self.__handles is None:
            return table

        self.verbose(f"Describing the table '{name}' ...'")
        for header in self.__handles[name][2]:
            table.add(name = header, type = "String")

        return table

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        if self.__handles is None:
            return []

        return DWHConnectorDatabaseEngineCSV.IteratorRecords(DWHConnectorDatabaseRecord(table), self.__handles[table.name])

    def close(self):
        """Close the connexion to the CSV files"""
        if self.__handles is None:
            super().close()
            return

        self.info("Closing the CSV files for read")
        for name, file in self.__handles.items():
            self.info(f"Closing the file '{name}' for read ...")
            file[0].close()

        self.__handles = None
        super().close()

    def __init__(self, name, files = {}, **kwargs):
        super().__init__(name, files = files)
        self.__handles = None
