# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

import datetime

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
        return None

    @property
    def is_null(self):
        """Get the null possible value of the field"""
        return self.__is_null

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

    def to_mysql(self, type_mysql):
        default_value = ""
        if not self.default_value is None:
            if isinstance(self.default_value, int):
                default_value = f" DEFAULT {self.default_value}"
            elif isinstance(self.default_value, bool):
                if self.default_value:
                    default_value = " DEFAULT 1"
                else:
                    default_value = " DEFAULT 0"
            elif isinstance(self.default_value, float):
                default_value = f" DEFAULT {self.default_value}"
            elif isinstance(self.default_value, datetime.datetime):
                default_value = f" DEFAULT {self.default_value}"
            else:
                default_value = f" DEFAULT '{self.default_value}'"

        not_null = ""
        if not self.is_null:
            not_null = " NOT NULL"

        return f"`{self.name}` {type_mysql}{default_value}{not_null}"

    def __init__(self, table, name, is_null, default_value):
        super().__init__(f"{table.connector.name}.{table.name}.{name}")
        self.__table = table
        self.__name = name
        self.__is_null = is_null
        self.__default_value = default_value
        self.__from_field = {}
