# -*- coding: utf-8 -*-

"""
This module describes a rule exception.
"""

from exception.exception import DWHException

class DWHExceptionRule(DWHException):
    """Rule exception"""

    @property
    def name(self):
        return self.__rule.name

    @property
    def record(self):
        return self.__record

    def __init__(self, rule, record):
        super().__init__("Rule not validated")
        self.__rule = rule
        self.__record = record.to_dict()
