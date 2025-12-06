# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from logger.loggerobject import DWHLoggerObject
from connector.database.field import DWHConnectorDatabaseField

class DWHConnectorDatabaseTable(DWHLoggerObject):
    """This class defines a table containing Fields"""

    @property
    def connector(self):
        """Get the connector of the table"""
        return self.__connector

    @property
    def name(self):
        """Get the name of the table"""
        return self.__name

    @property
    def fields(self):
        """Get the fields of the table"""
        return self.__fields

    @property
    def count_fields(self):
        """Get the number of fields in the table"""
        return len(self.__fields)

    @property
    def filter(self):
        return self.__filter

    @filter.setter
    def filter(self, filter):
        self.__filter = filter

    def add(self, field_name, field_type):
        if not field_name in self.__fields:
            self.__fields[field_name] = DWHConnectorDatabaseField(self, field_name, field_type)
        return self.__fields[field_name]

    def remove(self, field_name):
        if not field_name in self.__fields:
            return
        del self.__fields[field_name]

    @property
    def count_rows(self):
        return self.connector.count_rows(self.name, self.filter)

    def __init__(self, connector, name):
        super().__init__(f"{connector.name}.{name}")
        self.__connector = connector
        self.__name = name
        self.__filter = None
        self.__fields = {}
