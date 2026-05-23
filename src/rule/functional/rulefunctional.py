# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract functional rule.
"""

from tkinter import NO
from exception.exceptionrule import DWHExceptionRule

from rule.rule import DWHRule

class DWHRuleFunctional(DWHRule):
    """This class defines an abstract functional rule"""

    @property
    def description(self):
        return self.__description

    @property
    def table(self):
        return self.__table

    @property
    def field(self):
        return self.__field

    @property
    def filename(self):
        return self.__filename

    @property
    def email(self):
        return self.__email

    @property
    def order(self):
        return self.__order

    @property
    def limit(self):
        return self.__limit

    def execute(self, record):
        table = record.get_table()

        if record is None or table.name != self.table:
            return None

        if not (self.field in table.fields or self.field in table.extends):
            self.error(f"Field '{table.name}.{self.field.name}' doesn't exist in the table")
            raise DWHExceptionRule(self, None, record)

        return record

    def markdown(self, directory):
        """Get the markdown documentation of the rule"""
        return super().markdown(directory)

    def __init__(self, instance, name, table, field, description, notifications = None):
        super().__init__(name)
        self.__instance = instance
        self.__table = table
        self.__field = field
        self.__description = description

        self.__filename = None
        self.__email = None
        self.__order = None
        self.__limit = None

        if notifications is not None:
            self.__filename = notifications.get('filename', None)
            self.__email = notifications.get('email', None)
            self.__order = notifications.get('order', None)
            self.__limit = notifications.get('limit', None)
