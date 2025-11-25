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

    def __init__(self, table, field_name, field_type):
        super().__init__(f"{table.connector.name}.{table.name}.{field_name}")
        self.__table = table
        self.__name = field_name
        self.__type = field_type
