# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a rule checking if a value expected a regular expression and convert values.
"""

import re

from exception.exceptionrule import DWHExceptionRule

from rule.functional.rulefunctional import DWHRuleFunctional

class DWHRuleFunctionalRegex(DWHRuleFunctional):
    """This class defines a rule checking a regular expression and convert a part of values"""

    def execute(self, record):
        if record is None or record.get_table().name != self.table:
            return record

        value = record[self.field]
        if value is None:
            value = ""
        items = self.__regex.match(value)

        if items is None:
            raise DWHExceptionRule(self, record)

        for field, properties in self.__values.items():
            group_name = properties.get('name', None)
            if group_name is None:
                continue

            group_value = items.group(group_name)
            if group_value is None:
                continue

            values = properties.get('values', {})
            else_value = properties.get('else', None)

            if group_value in values:
                record[field] = values[group_value]
            elif else_value is None:
                record[field] = group_value
            else:
                record[field] = else_value

        return record

    def __init__(self, name, field, regex, description = "", values = {}, **kwargs):
        super().__init__(name, field, description)
        self.__regex = re.compile(regex)
        self.__values = values.to_dict()
