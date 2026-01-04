# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract technical rule.
"""

from rule.technical.ruletechnical import DWHRuleTechnical

class DWHRuleTechnicalIgnore(DWHRuleTechnical):
    """This class defines a technical rule to ignore the table"""

    @property
    def description(self):
        return "Nous ignorons la table car elle ne présente pas d'intérêts"

    @property
    def ignore(self):
        return True

    def execute(self, table):
        self.info(f"Ignoring table '{table.name}' ...")
        return False

    def markdown(self, table, directory):
        """Get the markdown documentation of the technical rule (ignoring this table)"""
        return super().markdown(table, directory)

    def __init__(self, name, **kwargs):
        super().__init__(name)
