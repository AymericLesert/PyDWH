# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract functional rule.
"""

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

    def execute(self, record):
        table = record.get_table()

        if record is None or table.name != self.table:
            return None

        if not (self.field in table.fields or self.field in table.extends):
            self.error(f"Field '{table.name}.{self.field.name}' doesn't exist in the table")
            raise DWHExceptionRule(self, record)

        return record

    def markdown(self, directory):
        """Get the markdown documentation of the rule"""
        return super().markdown(directory)

    def __init__(self, name, table, field, description):
        super().__init__(name)
        self.__table = table
        self.__field = field
        self.__description = description
