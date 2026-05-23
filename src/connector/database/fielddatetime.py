# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a datetime field.
"""

from connector.database.field import DWHConnectorDatabaseField
from tools.date import Date

class DWHConnectorDatabaseFieldDateTime(DWHConnectorDatabaseField):
    """This class defines a datetime field"""

    @property
    def type(self):
        """Get the type of the field"""
        return "DateTime"

    @property
    def format(self):
        """Get the format of the field"""
        return Date.DATETIME

    def copy(self, table):
        return DWHConnectorDatabaseFieldDateTime(table,
                                                 self.name,
                                                 self.is_null,
                                                 self.default_value,
                                                 self.description)

    def to_mysql(self):
        return super().to_mysql("datetime")

    def to_SQLServer(self):
        return super().to_SQLServer("datetime")

    def to_PostgreSQL(self):
        return super().to_PostgreSQL("time without time zone")

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        return value

    def __init__(self, table, name, is_null = True, default_value = None, description = "", **kwargs):
        if not is_null and default_value is None:
            default_value = Date.NOW
        super().__init__(table, name, is_null, default_value, description)
