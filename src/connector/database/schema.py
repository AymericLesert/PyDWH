# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from logger.loggerobject import DWHLoggerObject
from connector.database.table import DWHConnectorDatabaseTable

class DWHConnectorDatabaseSchema(DWHLoggerObject):
    """This class defines a schema containing Tables and Fields"""

    @property
    def name(self):
        """Get the name of the schema"""
        return self.__name

    @property
    def tables(self):
        """Get the tables of the schema"""
        return self.__tables

    @property
    def count_tables(self):
        """Get the number of tables in the schema"""
        return len(self.__tables)

    @property
    def count_fields(self):
        """Get the number of fields in the schema"""
        count = 0
        for table in self.__tables.values():
            count += table.count_fields
        return count

    def add(self, connector, table_name):
        new_table = DWHConnectorDatabaseTable(connector, table_name)
        self.__tables[new_table.name] = new_table
        return new_table

    def append(self, schema):
        for table in schema.tables.values():
            new_table = DWHConnectorDatabaseTable(table.connector, table.name)
            self.__tables[new_table.name] = new_table
            for field_name, field in table.fields.items():
                new_table.add(field_name, field.type)

    def remove(self, name):
        if not name in self.__tables:
            return
        del self.__tables[name]

    def __init__(self, name):
        super().__init__(name)
        self.__name = name
        self.__tables = {}
