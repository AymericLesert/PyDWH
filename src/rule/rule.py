# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract rule.
"""

from logger.loggerobject import DWHLoggerObject

class DWHRule(DWHLoggerObject):
    """This class defines an abstract rule"""

    @property
    def name(self):
        """Get the name of the rule"""
        return self.__name

    @property
    def description(self):
        """Get the description of the rule"""
        return ""

    @property
    def ignore(self):
        """Indicates if the rule has to be ignored"""
        return False

    def execute(self, table):
        """Define the rule checking values from a table"""
        return False

    def __init__(self, name):
        super().__init__(name)
        self.__name = name
