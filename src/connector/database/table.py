# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from logger.loggerobject import DWHLoggerObject
from connector.database.field import DWHConnectorDatabaseField

class DWHConnectorDatabaseTable(DWHLoggerObject):
    """This class defines a table containing Fields"""

    def verbose(self, message):
        super().verbose(f"[{self.instance.name}.{self.name}] {message}")

    def debug(self, message):
        super().debug(f"[{self.instance.name}.{self.name}] {message}")

    def info(self, message):
        super().info(f"[{self.instance.name}.{self.name}] {message}")

    def warning(self, message):
        super().warning(f"[{self.instance.name}.{self.name}] {message}")

    def error(self, message):
        super().error(f"[{self.instance.name}.{self.name}] {message}")

    def critical(self, message):
        super().critical(f"[{self.instance.name}.{self.name}] {message}")

    def exception(self, message):
        super().exception(f"[{self.instance.name}.{self.name}] {message}")

    @property
    def instance(self):
        """Get the instance of the table"""
        return self.__instance

    @property
    def name(self):
        """Get the name of the table"""
        return self.__name

    @property
    def fields(self):
        """Get the fields of the table"""
        return self.__fields

    def add_field(self, field_name, field_type):
        if not field_name in self.__fields:
            self.__fields[field_name] = DWHConnectorDatabaseField(self, field_name, field_type)
        return self.__fields[field_name]

    def __init__(self, instance, name):
        super().__init__()
        self.__instance = instance
        self.__name = name
        self.__fields = {}
