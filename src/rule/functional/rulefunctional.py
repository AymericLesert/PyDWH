# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract functional rule.
"""

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
        return record

    def __init__(self, name, field, description):
        super().__init__(name)
        self.__table, self.__field = field.split('.', 1)
        self.__description = description
