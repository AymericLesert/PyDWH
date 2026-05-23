# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a string field.
"""

import re

from connector.database.field import DWHConnectorDatabaseField
from exception.exceptionrecordfieldinvalid import DWHExceptionRecordFieldInvalid

class DWHConnectorDatabaseFieldString(DWHConnectorDatabaseField):
    """This class defines a string field"""

    @property
    def type(self):
        """Get the type of the field"""
        return "String"

    @property
    def default_value(self):
        """Get the default value of the field"""
        if not super().is_null and super().default_value is None:
            return ""
        return super().default_value

    @property
    def length(self):
        """Get the max length of the field"""
        return self.__length

    @property
    def format(self):
        """Get the format of the field"""
        if self.length == 0:
            return "Unlimited length"
        return f"Max length {self.length}"

    @property
    def regex(self):
        return self.__regex

    @regex.setter
    def regex(self, value):
        self.__regex = value
        if value is None:
            self.__re = None
        else:
            self.__re = re.compile(value)

    def copy(self, table):
        return DWHConnectorDatabaseFieldString(table,
                                               self.name,
                                               self.length,
                                               self.is_null,
                                               self.default_value,
                                               self.description)

    def check(self, value):
        if self.__re is None:
            return

        if value is None:
            value  = ''

        if self.__re.match(value):
            return

        raise DWHExceptionRecordFieldInvalid(self, f"'{value}' does not match the regex '{self.__regex}'")

    def to_mysql(self):
        return super().to_mysql(f"varchar({self.length})")

    def to_SQLServer(self):
        return super().to_SQLServer(f"nvarchar({self.length})")

    def to_PostgreSQL(self):
        return super().to_PostgreSQL(f"varchar({self.length})")

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        if isinstance(value, str):
            return value.strip()
        return value

    def __init__(self, table, name, length = 0, is_null = True, default_value = None, description = "", **kwargs):
        super().__init__(table, name, is_null, default_value, description)
        self.__length = length if length is not None else 0
        self.__regex = None
        self.__re = None
