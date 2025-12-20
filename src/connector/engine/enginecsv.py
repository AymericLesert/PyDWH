# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the engine for mysql.
"""

import csv

from connector.engine.engine import DWHConnectorDatabaseEngine
from connector.database.record import DWHConnectorDatabaseRecord

from dotenv import load_dotenv
from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger

class DWHConnectorDatabaseEngineCSV(DWHConnectorDatabaseEngine):
    """This class defines a csv engine"""

    class IteratorRecords:
        def __iter__(self):
            return self

        def __next__(self):
            self.__record.clear()

            row = next(self.__csv_handle)

            table = self.__record.get_table()
            for i, field in enumerate(table.fields.values()):
                if field.type is None:
                    self.__record[field.name] = None
                else:
                    self.__record[field.name] = row[i]

            return self.__record

        def __init__(self, record, csv_handle):
            self.__record = record
            self.__csv_handle = csv_handle

    def get_request_insert(self, table):
        """Build SQL request"""

        list_fields = ', '.join([f"`{field}`" for field in table.keys] + [f"`{field}`" for field in table.fields if field not in table.keys])
        list_values = ', '.join(["%s" for _ in table.fields])

        return f"INSERT INTO `{table.name}` ({list_fields}, `DWHAction`, `DWHDateHeure`) VALUES (%s, %s, {list_values})"

    def get_file(self, name):
        file = self.__files[name]
        handle = open(file['filename'], newline='', encoding=file.get('encoding', 'ansi'))
        csv_handle = csv.reader(handle, delimiter = file.get('delimiter', ','), quoting = file.get('quoting', csv.QUOTE_NONE))
        return [handle, csv_handle, next(csv_handle)]

    def open(self):
        """Connect to the CSV Files"""
        super().open()
        self.info("Connecting to CSV files")
        self.__handles = {}
        for name, file in self.__files.items():
            self.info(f"Openning the file '{name}' - '{file["filename"]}' ...")
            try:
                self.__handles[name] = self.get_file(name)
            except StopIteration:
                self.info("File empty")
            except:
                self.exception("Unable to open file")

    def create_dwh(self):
        pass

    def create_table(self, table):
        # TODO : Create a new CSV file
        pass

    def update_table(self, table):
        # TODO : Update a file if the target exists ...
        pass

    def remove_table(self, table):
        # TODO : Remove a file or move it
        pass

    def get_tables(self):
        if self.__handles is None:
            return []

        return [name for name in self.__handles]

    def get_table(self, name):
        if self.__handles is None:
            return super().get_table(name)

        self.verbose(f"Describing the table '{name}' ...'")
        table = super().get_table(name)
        _, _, headers = self.__handles[name]

        for column in headers:
            table.add(name = column, type = "String")

        return table

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        if self.__handles is None:
            return []

        return DWHConnectorDatabaseEngineCSV.IteratorRecords(DWHConnectorDatabaseRecord(table), self.__handles[table.name][1])

    def count_rows(self, table_name, filter = None):
        # table_name is a name of an existing table ... by design (no risk of injection from configuration file)
        if self.__handles is None:
            return 0

        try:
            handle, csv_handle, _ = self.get_file(table_name)
        except StopIteration:
            return 0

        try:
            count_rows = 0
            for row in csv_handle:
                count_rows += 1
        finally:
            handle.close()

        return 0 if count_rows <= 0 else count_rows - 1

    def close(self):
        """Close the connexion to the CSV files"""
        if self.__handles is not None:
            self.info("Closing to the CSV files")
            for name, file in self.__handles.items():
                self.info(f"Closing the file '{name}' - '{self.__files[name]['filename']}' ...")
                file[0].close()
            self.__handles = None
        super().close()

    def __init__(self, name, files = {}, **kwargs):
        super().__init__(name)
        if files is None:
            self.__files = {}
        elif isinstance(files, dict):
            self.__files = files
        else:
            self.__files = files.to_dict()
        self.__handles = None


if __name__ == "__main__":
    # Charge les variables d'environnement depuis le fichier .env (dont les logins / mots de passe)

    load_dotenv()

    # Charge le fichier de configuration
    
    configuration = DWHConfiguration("../PyDWHConfig/config.yml")

    # Initialise le logger

    logger = DWHLogger(configuration)
    logger.open()

    engine = DWHConnectorDatabaseEngineCSV("CSV", files = { "OF": { "filename": "D:\\024 - Team Plastique\\DWH\\ECMA\\OF.csv", "delimiter": ";", "encoding": "utf-8" } })
    engine.open()
    engine.info(engine.get_tables())
    for name in engine.get_tables():
        engine.info(f"Nb rows : {engine.count_rows(name)}")
        for row in engine.get_table(name):
            engine.info(row.to_dict())
    engine.close()

    logger.close()