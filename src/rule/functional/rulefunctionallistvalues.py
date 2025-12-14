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

        if record[self.field] not in self.__values:
            raise DWHExceptionRule(self, record)

        return record

    def __init__(self, name, table, field, description = "", values = [], **kwargs):
        super().__init__(name, table, field, description)
        self.__values = values
