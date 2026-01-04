# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a double field.
"""

from connector.database.field import DWHConnectorDatabaseField

class DWHConnectorDatabaseFieldDouble(DWHConnectorDatabaseField):
    """This class defines a double field"""

    @property
    def type(self):
        """Get the type of the field"""
        return "Double"

    @property
    def length(self):
        """Get the max number of digits of the field"""
        return self.__length

    @property
    def decimal(self):
        """Get the decimal of the field"""
        return self.__decimal   

    @property
    def format(self):
        """Get the format of the field"""
        return f"{self.length-self.decimal}.{self.decimal}"

    def copy(self, table):
        return DWHConnectorDatabaseFieldDouble(table,
                                               self.name,
                                               self.length,
                                               self.decimal,
                                               self.is_null,
                                               self.default_value,
                                               self.description)

    def to_mysql(self):
        return super().to_mysql(f"decimal({self.length+self.decimal},{self.decimal})")

    def to_SQLServer(self):
        return super().to_SQLServer(f"decimal({self.length+self.decimal},{self.decimal})")

    def to_PostgreSQL(self):
        return super().to_PostgreSQL(f"decimal({self.length+self.decimal},{self.decimal})")

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        return value

    def __init__(self, table, name, length = 8, decimal = 4, is_null = True, default_value = None, description = "", **kwargs):
        if not is_null and default_value is None:
            default_value = 0
        super().__init__(table, name, is_null, default_value, description)
        self.__length = length
        self.__decimal = decimal
