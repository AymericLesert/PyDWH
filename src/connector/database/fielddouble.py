# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from connector.database.field import DWHConnectorDatabaseField

class DWHConnectorDatabaseFieldDouble(DWHConnectorDatabaseField):
    """This class defines a double field"""

    @property
    def type(self):
        """Get the type of the field"""
        return "Double"

    def to_mysql(self):
        return super().to_mysql(f"decimal({self.length+self.decimal},{self.decimal})")

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        return value

    def __init__(self, table, name, length = 8, decimal = 4, is_null = True, default_value = None, **kwargs):
        if not is_null and default_value is None:
            default_value = 0
        super().__init__(table, name, is_null, default_value)
        self.__length = length
        self.__decimal = decimal
