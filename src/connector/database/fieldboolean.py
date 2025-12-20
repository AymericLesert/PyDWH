# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a boolean field.
"""

from connector.database.field import DWHConnectorDatabaseField

class DWHConnectorDatabaseFieldBoolean(DWHConnectorDatabaseField):
    """This class defines a boolean field"""

    @property
    def type(self):
        """Get the type of the field"""
        return "Boolean"

    def to_mysql(self):
        return super().to_mysql("tinyint")

    def to_SQLServer(self):
        return super().to_SQLServer("int")

    def to_PostgreSQL(self):
        return super().to_PostgreSQL("boolean")

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        return value

    def __init__(self, table, name, is_null = True, default_value = None, **kwargs):
        if not is_null and default_value is None:
            default_value = False
        super().__init__(table, name, is_null, default_value)
