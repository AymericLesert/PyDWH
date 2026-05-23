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
        if super().execute(record) is None:
            return None

        value = record[self.field]
        if value is None:
            value = ""
        value = value.strip()
        items = self.__regex.match(value)

        if items is None:
            raise DWHExceptionRule(self, value, record)

        for field, properties in self.__values.items():
            group_name = properties.get('name', None)
            if group_name is None:
                continue

            try:
                group_value = items.group(group_name)
                if group_value is None:
                    continue
            except:
                raise DWHExceptionRule(self, value, record)

            values = properties.get('values', {})
            else_value = properties.get('else', None)

            if group_value in values:
                record[field] = values[group_value]
            elif else_value is None:
                record[field] = group_value
            else:
                record[field] = else_value

        return record

    def markdown(self, directory):
        """Get the markdown documentation of the rule"""
        # TODO
        return super().markdown(directory)

    def __init__(self, instance, name, table, field, regex, description = "", notifications = None, values = {}, **kwargs):
        super().__init__(instance, name, table, field, description, notifications)
        self.__regex = re.compile(regex)
        self.__values = values.to_dict() if not isinstance(values, dict) else values
