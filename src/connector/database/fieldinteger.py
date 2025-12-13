# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from connector.database.field import DWHConnectorDatabaseField

class DWHConnectorDatabaseFieldInteger(DWHConnectorDatabaseField):
    """This class defines an integer field"""

    @property
    def type(self):
        """Get the type of the field"""
        return "Integer"

    def to_mysql(self):
        return super().to_mysql("int")

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        return value

    def __init__(self, table, name, is_null = True, default_value = None, **kwargs):
        if not is_null and default_value is None:
            default_value = 0
        super().__init__(table, name, is_null, default_value)
