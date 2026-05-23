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
    def rule(self):
        return self.__rule

    @property
    def value(self):
        return self.__value

    @property
    def record(self):
        return self.__record

    def __init__(self, rule, value, record):
        super().__init__("Rule not validated")
        self.__rule = rule
        self.__record = record.to_dict()
        self.__value = value
