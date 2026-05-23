# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the engine for writing csv files.
"""

import csv
import os

from connector.engine.enginecsv import DWHConnectorDatabaseEngineCSV
from connector.database.record import DWHConnectorDatabaseRecord

class DWHConnectorDatabaseEngineCSVWriter(DWHConnectorDatabaseEngineCSV):
    """This class defines a writing csv engine"""

    @property
    def handles(self):
        return self.__handles

    def get_request_insert(self, table):
        return table.name

    def open(self):
        """Open the CSV Files for writing"""
        super().open()
        self.info("Openning the CSV files for writing")
        self.__handles = []

        # Select only tables described into the CSV configuration

        for name in [name for name in self.__schema.tables if name not in self.files]:
            self.__schema.remove(name)

    def create_table(self, table):
        """Create a CSV file within the header"""
        super().create_table(table)
        try:
            handle = self.get_file(table.name, DWHConnectorDatabaseEngineCSV.CSVWrite)
            handle[1].writerow(list(table.fields.keys()) + ["DWHAction", "DWHDateHeure"])
            handle[0].close()
        except:
            self.exception("Unable to create the file")

    def update_table(self, table):
        # Update a file if the target exists ...

        super().update_table(table)

        # Retrieve the description of the existing table

        existing_table = self.get_table(table.name, table.description)
        existing_fields = sorted([ field.name for field in existing_table.fields.values() ])

        # Check if the header changes

        new_fields = sorted([ field.name for field in table.fields.values() ] + ["DWHAction", "DWHDateHeure"])
        if existing_fields == new_fields:
            return

        # Read the old file

        self.verbose(f"Updating the file '{table.name}' ...")

        rows = [[name for name in table.fields] + ["DWHAction", "DWHDateHeure"]]
        try:
            handle = self.get_file(table.name)

            new_record = DWHConnectorDatabaseRecord(table)
            for old_record in DWHConnectorDatabaseEngineCSV.IteratorRecords(DWHConnectorDatabaseRecord(existing_table), handle):
                row = []
                for field in table.fields.values():
                    if field.name in existing_table.fields or field.name in ["DWHAction", "DWHDateHeure"]:
                        row.append(old_record[field.name])
                    else:
                        row.append(field.default_value)
                rows.append(row)
            handle[0].close()
        except StopIteration:
            pass

        self.verbose(f"Reading {len(rows)} rows ...")

        # Rewrite the new file

        handle = self.get_file(table.name, DWHConnectorDatabaseEngineCSV.CSVWrite)
        handle[1].writerows(rows)
        handle[0].close()

        self.verbose(f"Writing {len(rows)} rows ...")

    def remove_table(self, table):
        """Remove a csv file"""
        super().remove_table(table)

        if table.name not in self.files:
            return

        file = self.files[table.name]
        
        filename = file['filename']
        self.verbose(f"Removing file '{filename}' ...")

        if not os.path.exists(filename) or not os.path.isfile(filename):
            return
        
        try:
            os.remove(filename)
        except:
            self.exception("Unable to remove the file")

    def get_tables(self):
        tables = []
        for name, configuration in self.files.items():
            filename = configuration['filename']
            self.verbose(filename)
            if os.path.exists(filename) and os.path.isfile(filename):
                tables.append(name)
        return tables

    def get_table(self, name, description):
        table = super().get_table(name, description)
        if name not in self.files:
            return table

        self.verbose(f"Describing the table '{name}' ...'")

        filename = self.files[name]['filename']
        if not os.path.exists(filename) or not os.path.isfile(filename):
            self.error(f"File '{filename}' not found")
            return table

        try:
            handle, _, headers = self.get_file(name, DWHConnectorDatabaseEngineCSV.CSVRead)
        except:
            self.error("Unable to read the header")
            return table

        for column in headers:
            table.add(name = column, type = "String")

        handle.close()

        return table

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        if table.name not in self.files:
            return []

        try:
            handle = self.get_file(table.name, DWHConnectorDatabaseEngineCSV.CSVRead)
            self.__handles.append(handle)
            return DWHConnectorDatabaseEngineCSV.IteratorRecords(DWHConnectorDatabaseRecord(table), handle)
        except:
            return []

    def execute(self, request, values = None):
        super().execute(request, values)
        if values is None:
            return

        # Append the content into the file

        handle = self.get_file(request, DWHConnectorDatabaseEngineCSV.CSVAdd)
        handle[1].writerows(values)
        handle[0].close()

        self.verbose(f"Writing {len(values)} rows ...")

    def close(self):
        """Close the connexion to the CSV files"""
        if self.__handles is not None:
            self.info("Closing the CSV files ...")
            for handle in self.__handles:
                handle[0].close()
            self.__handles = None
        super().close()

    def __init__(self, name, files = {}, schema = None, **kwargs):
        super().__init__(name, files = files)
        self.__schema = schema
        self.__handles = None
