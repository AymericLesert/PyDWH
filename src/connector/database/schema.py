# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from logger.loggerobject import DWHLoggerObject
from connector.database.table import DWHConnectorDatabaseTable

class DWHConnectorDatabaseSchema(DWHLoggerObject):
    """This class defines a schema containing Tables and Fields"""

    def verbose(self, message):
        super().verbose(f"[{self.name}] {message}")

    def debug(self, message):
        super().debug(f"[{self.name}] {message}")

    def info(self, message):
        super().info(f"[{self.name}] {message}")

    def warning(self, message):
        super().warning(f"[{self.name}] {message}")

    def error(self, message):
        super().error(f"[{self.name}] {message}")

    def critical(self, message):
        super().critical(f"[{self.name}] {message}")

    def exception(self, message):
        super().exception(f"[{self.name}] {message}")

    @property
    def name(self):
        """Get the name of the schema"""
        return self.__name

    @property
    def tables(self):
        """Get the tables of the schema"""
        return self.__tables

    def add_table(self, table_name):
        if not table_name in self.__tables:
            self.__tables[table_name] = DWHConnectorDatabaseTable(self, table_name)
        return self.__tables[table_name]

    def append(self, schema):
        for table_name, table in schema.tables.items():
            new_table = DWHConnectorDatabaseTable(self, table_name)
            self.tables[table_name] = new_table
            for field_name, field in table.fields.items():
                new_table.add_field(field_name, field.type)
        pass

    def __init__(self, name):
        super().__init__()
        self.__name = name
        self.__tables = {}
