# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a rule checking if a value is included into the list of values.
"""

from exception.exceptionrule import DWHExceptionRule

from rule.functional.rulefunctional import DWHRuleFunctional

class DWHRuleFunctionalListValues(DWHRuleFunctional):
    """This class defines a rule checking if a value is included into the list of values"""

    def execute(self, record):
        if super().execute(record) is None:
            return None

        value = record[self.field].strip()
        if value not in self.__values:
            raise DWHExceptionRule(self, value, record)

        return record

    def markdown(self, directory):
        """Get the markdown documentation of the rule"""
        # TODO
        return super().markdown(directory)

    def __init__(self, instance, name, table, field, description = "", notifications = None, values = [], **kwargs):
        super().__init__(instance, name, table, field, description, notifications)
        self.__values = values
