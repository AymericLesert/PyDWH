# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract rule.
"""

from logger.loggerobject import DWHLoggerObject

class DWHRule(DWHLoggerObject):
    """This class defines an abstract rule"""
    # TODO : Implement a rule described into the project
    # - Field(s)
    # - Description
    # - Rule
    # - Sender of the non-respect of the rule (technical, functional, ...)
    # - Filter to apply to the non-respect
    # - Confidentiality level
    # - List of users allowed to see the value

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

    def execute(self):
        """Execute a technical or functional rule"""
        return False

    def markdown(self, directory):
        """Get the markdown documentation of the rule"""
        return None

    def __init__(self, name):
        super().__init__(name)
        self.__name = name
