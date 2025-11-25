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
        for table in self.__tables:
            count += table.count_fields
        return count

    def add_table(self, connector, table_name):
        new_table = DWHConnectorDatabaseTable(connector, table_name)
        self.__tables.append(new_table)
        return new_table

    def append(self, schema):
        for table in schema.tables:
            new_table = DWHConnectorDatabaseTable(table.connector, table.name)
            self.__tables.append(new_table)
            for field_name, field in table.fields.items():
                new_table.add_field(field_name, field.type)

    def __init__(self, name):
        super().__init__(name)
        self.__name = name
        self.__tables = []
