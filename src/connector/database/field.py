# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from logger.loggerobject import DWHLoggerObject

class DWHConnectorDatabaseField(DWHLoggerObject):
    """This class defines a field"""

    def verbose(self, message):
        super().verbose(f"[{self.instance.name}.{self.table.name}.{self.name}] {message}")

    def debug(self, message):
        super().debug(f"[{self.instance.name}.{self.table.name}.{self.name}] {message}")

    def info(self, message):
        super().info(f"[{self.instance.name}.{self.table.name}.{self.name}] {message}")

    def warning(self, message):
        super().warning(f"[{self.instance.name}.{self.table.name}.{self.name}] {message}")

    def error(self, message):
        super().error(f"[{self.instance.name}.{self.table.name}.{self.name}] {message}")

    def critical(self, message):
        super().critical(f"[{self.instance.name}.{self.table.name}.{self.name}] {message}")

    def exception(self, message):
        super().exception(f"[{self.instance.name}.{self.table.name}.{self.name}] {message}")

    @property
    def instance(self):
        """Get the instance of the field"""
        return self.table.instance

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
        super().__init__()
        self.__table = table
        self.__name = field_name
        self.__type = field_type
