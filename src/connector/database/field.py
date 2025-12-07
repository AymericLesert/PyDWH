# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from logger.loggerobject import DWHLoggerObject

class DWHConnectorDatabaseField(DWHLoggerObject):
    """This class defines a field"""

    @property
    def table(self):
        """Get the table of the field"""
        return self.__table

    @property
    def name(self):
        """Get the name of the field"""
        return self.__name

    @property
    def type(self):
        """Get the type of the field"""
        return self.__type

    @property
    def default_value(self):
        """Get the default value of the field"""
        return self.__default_value

    @property
    def from_fields(self):
        return self.__from_fields

    @from_fields.setter
    def from_fields(self, from_fields):
        self.__from_fields = {}

        for field in from_fields:
            table_name, field_name = field.split('.', 1)
            if table_name not in self.__from_fields:
                self.__from_fields[table_name] = []
            self.__from_fields[table_name].append(field_name)

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        return value

    def __init__(self, table, field_name, field_type):
        super().__init__(f"{table.connector.name}.{table.name}.{field_name}")
        self.__table = table
        self.__name = field_name
        self.__type = field_type
        self.__default_value = None
        self.__from_field = {}
