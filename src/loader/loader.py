# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the loader component.
"""

from logger.loggerobject import DWHLoggerObject

class DWHLoader(DWHLoggerObject):
    """This class defines an abstract loader"""

    @property
    def name(self):
        """Get the name of the source"""
        return self.__name

    @property
    def description(self):
        """Get the description of the source"""
        return { "name": self.name }

    def __enter__(self):
        """Open a new instance of the loader"""
        self.open()

    def __exit__(self, *args):
        """Close the instance of the loader"""
        self.close()

    def open(self):
        self.info(f"[{self.name}] Openning the loader ...")

    def close(self):
        self.info(f"[{self.name}] Closing the loader ...")

    def __init__(self, name):
        super().__init__()
        self.__name = name
