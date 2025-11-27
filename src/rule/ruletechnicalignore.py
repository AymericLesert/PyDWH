# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract technical rule.
"""

from rule.ruletechnical import DWHRuleTechnical

class DWHRuleTechnicalIgnore(DWHRuleTechnical):
    """This class defines a technical rule to ignore the table"""

    @property
    def description(self):
        return "Comme la table ne présente pas d'intérêts, nous allons l'ignorer."

    def execute(self, table):
        self.info(f"Ignoring table '{table.name}' ...")
        return False

    def __init__(self, name):
        super().__init__(name)
