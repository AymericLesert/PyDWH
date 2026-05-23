# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the engine for csv files.
"""

import csv
import os

from connector.engine.engine import DWHConnectorDatabaseEngine
from connector.database.record import DWHConnectorDatabaseRecord

class DWHConnectorDatabaseEngineCSV(DWHConnectorDatabaseEngine):
    """This class defines a csv engine"""

    CSVRead = 0
    CSVWrite = 1
    CSVAdd = 2

    class IteratorRecords:
        def __iter__(self):
            return self

        def __next__(self):
            self.__record.clear()

            table = self.__record.get_table()
            row = next(self.__handle[1])

            for i, header in enumerate(self.__handle[2]):
                if header in table.fields:
                    self.__record[header] = row[i]
                if header == "DWHAction":
                    self.__record.set_action(row[i])
                if header == "DWHDateHeure":
                    self.__record.set_datetime(row[i])

            return self.__record

        def __init__(self, record, handle):
            self.__record = record
            self.__handle = handle

    @property
    def type(self):
        """Type of the source"""
        return "CSV"

    @property
    def properties(self):
        """Properties of the source"""
        return [(name, properties) for name, properties in self.__files.items()]

    @property
    def files(self):
        return self.__files

    @property
    def handles(self):
        return None

    def get_file(self, name, mode = CSVRead):
        if name not in self.__files:
            return [None, None, None]

        file = self.__files[name]
        
        handle = None
        csv_handle = None
        header = []

        if mode == DWHConnectorDatabaseEngineCSV.CSVRead:
            self.verbose(f"Reading the file '{file['filename']}' ...")
            handle = open(file['filename'], 'r', newline='', encoding=file.get('encoding', 'ansi'))
            csv_handle = csv.reader(handle, delimiter = file.get('delimiter', ','), quoting = file.get('quoting', csv.QUOTE_NONE))
            header = next(csv_handle)
        elif mode == DWHConnectorDatabaseEngineCSV.CSVWrite:
            self.verbose(f"Writing the file '{file['filename']}' ...")

            directory = os.path.dirname(file['filename'])
            if directory != '':
                try:
                    os.makedirs(directory, exist_ok=True)
                except:
                    pass

            handle = open(file['filename'], 'w', newline='', encoding=file.get('encoding', 'ansi'))
            csv_handle = csv.writer(handle, delimiter = file.get('delimiter', ','), quoting = file.get('quoting', csv.QUOTE_NONE))
            header = []
        elif mode == DWHConnectorDatabaseEngineCSV.CSVAdd:
            self.verbose(f"Writing the file '{file['filename']}' ...")

            directory = os.path.dirname(file['filename'])
            if directory != '':
                try:
                    os.makedirs(directory, exist_ok=True)
                except:
                    pass

            handle = open(file['filename'], 'a', newline='', encoding=file.get('encoding', 'ansi'))
            csv_handle = csv.writer(handle, delimiter = file.get('delimiter', ','), quoting = file.get('quoting', csv.QUOTE_NONE))
            header = []

        return [handle, csv_handle, header]

    def open(self):
        """Open the CSV Files"""
        super().open()

    def create_dwh(self):
        # Do not create the table DWHAction
        pass

    def create_table(self, table):
        super().create_table(table)

    def update_table(self, table):
        super().update_table(table)

    def remove_table(self, table):
        super().remove_table(table)

    def get_tables(self):
        return [name for name in self.__files]

    def get_table(self, name, description):
        return super().get_table(name, description)

    def read(self, table):
        return super().read(table)

    def count_rows(self, table_name, filter = None):
        if self.handles is None:
            return 0

        try:
            handle, csv_handle, _ = self.get_file(table_name, DWHConnectorDatabaseEngineCSV.CSVRead)
        except StopIteration:
            return 0

        try:
            count_rows = 0
            for _ in csv_handle:
                count_rows += 1
        finally:
            handle.close()

        return 0 if count_rows <= 0 else count_rows - 1

    def get_distinct_values(self, table_name, field_name, filter = None):
        if self.handles is None:
            return []

        try:
            handle, csv_handle, header = self.get_file(table_name, DWHConnectorDatabaseEngineCSV.CSVRead)
        except StopIteration:
            return []

        values = {}
        try:
            index_field = header.index(field_name)
            for row in csv_handle:
                value = row[index_field]
                if value not in values:
                    values[value] = 0
                values[value] += 1
        finally:
            handle.close()

        return [[value, count] for value, count in values.items()]

    def close(self):
        """Close the CSV files"""
        super().close()

    def __init__(self, name, files = {}, **kwargs):
        super().__init__(name)
        if files is None:
            self.__files = {}
        elif isinstance(files, dict):
            self.__files = files
        else:
            self.__files = files.to_dict()
