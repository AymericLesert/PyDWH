# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract technical rule.
"""

from rule.rule import DWHRule

class DWHRuleTechnical(DWHRule):
    """This class defines an abstract technical rule"""

    @property
    def description(self):
        return ""

    def execute(self, table):
        return False

    def __init__(self, name):
        super().__init__(name)
