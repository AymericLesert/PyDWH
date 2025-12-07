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
        if record is None or record.get_table().name != self.table:
            return record

        if not record[self.field] in self.__values:
            raise DWHExceptionRule(self, record)

        return record

    def __init__(self, name, field, description = "", values = [], **kwargs):
        super().__init__(name, field, description)
        self.__values = values
