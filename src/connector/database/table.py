# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from logger.loggerobject import DWHLoggerObject

from connector.database.field import DWHConnectorDatabaseField
from connector.database.fieldstring import DWHConnectorDatabaseFieldString
from connector.database.fieldinteger import DWHConnectorDatabaseFieldInteger
from connector.database.fielddouble import DWHConnectorDatabaseFieldDouble
from connector.database.fieldboolean import DWHConnectorDatabaseFieldBoolean
from connector.database.fielddate import DWHConnectorDatabaseFieldDate
from connector.database.fielddatetime import DWHConnectorDatabaseFieldDateTime

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
    def extends(self):
        """Get the extended fields of the table"""
        return self.__extends

    @property
    def fields_no_keys(self):
        if self.__fields_no_keys is None:
            self.__fields_no_keys = [name for name in self.__fields if name not in self.__keys]
            self.__fields_no_keys.extend([name for name in self.__extends if name not in self.__keys])
        return self.__fields_no_keys

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, keys):
        self.__keys = keys

    @property
    def filter(self):
        return self.__filter

    @filter.setter
    def filter(self, filter):
        self.__filter = filter

    @property
    def from_tables(self):
        return self.__from_tables

    @from_tables.setter
    def from_tables(self, from_tables):
        self.__from_tables = from_tables

    @property
    def count_fields(self):
        """Get the number of fields in the table"""
        return len(self.__fields)

    def add(self, name, type = "String", length = None, decimal = None, is_null = True, default_value = None, **kwargs):
        if name not in self.__fields:
            try:
                klass = eval(f"DWHConnectorDatabaseField{type}")
            except:
                self.error(f"Type '{type}' of the field '{name}' not implemented")
                return None

            self.__fields[name] = klass(self, name = name, 
                                              length = length,
                                              decimal = decimal, 
                                              is_null = is_null,
                                              default_value = default_value)
        return self.__fields[name]

    def extend(self, name, type = "String", length = None, decimal = None, is_null = True, default_value = None, **kwargs):
        if name not in self.__fields:
            try:
                klass = eval(f"DWHConnectorDatabaseField{type}")
            except:
                self.error(f"Type '{type}' of the field '{name}' not implemented")
                return None

            self.__extends[name] = klass(self, name = name, 
                                               length = length,
                                               decimal = decimal, 
                                               is_null = is_null,
                                               default_value = default_value)
        return self.__extends[name]

    def remove(self, field_name):
        if field_name not in self.__fields:
            return
        del self.__fields[field_name]

    @property
    def count_rows(self):
        return self.connector.count_rows(self.name, self.filter)

    def clear(self):
        self.__rows.clear()

    def store(self, record):
        if record is None:
            return

        self.__rows.append((record.to_values_keys(), record.to_values_fields()))

    @property
    def rows(self):
        return self.__rows

    def __iter__(self):
        """Iterator on the records from the table"""
        return self.connector.read(self)

    def __init__(self, connector, name):
        super().__init__(f"{connector.name}.{name}")
        self.__connector = connector
        self.__name = name
        self.__filter = None
        self.__fields = {}
        self.__extends = {}
        self.__keys = []
        self.__fields_no_keys = None

        self.__from_tables = None
        self.__rows = []
