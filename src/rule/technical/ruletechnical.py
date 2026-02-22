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

    def send_mail(self, to_addrs, subject, content, filename = None):
        if to_addrs is None or self.__instance is None:
            self.verbose("No mail sent")
            return 0

        return self.__instance.send_mail(to_addrs, subject, content, filename)

    def markdown(self, table, directory):
        """Get the markdown documentation of the technical rule"""
        return super().markdown(directory)

    def __init__(self, instance, name):
        super().__init__(name)
        self.__instance = instance
