# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a json field.
"""

import json
from connector.database.field import DWHConnectorDatabaseField

class DWHConnectorDatabaseFieldJSON(DWHConnectorDatabaseField):
    """This class defines a json field"""

    @property
    def type(self):
        """Get the type of the field"""
        return "JSON"

    @property
    def default_value(self):
        """Get the default value of the field"""
        if not super().is_null and super().default_value is None:
            return {}
        return super().default_value

    def to_mysql(self):
        return super().to_mysql(f"varchar({self.length})")

    def to_SQLServer(self):
        return super().to_SQLServer(f"nvarchar({self.length})")

    def to_PostgreSQL(self):
        return super().to_PostgreSQL("json")

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        if isinstance(value, str):
            return json.loads(value.strip())
        return value

    def __init__(self, table, name, length = 0, is_null = True, default_value = None, **kwargs):
        super().__init__(table, name, is_null, default_value)
