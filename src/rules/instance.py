# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the list of instances.
"""

from logger.loggerobject import DWHLoggerObject

class DWHInstance(DWHLoggerObject):
    @property
    def name(self):
        """Get the name of the instance"""
        return self.__name

    def __enter__(self):
        """Open a new instance"""
        self.open()

    def __exit__(self, *args):
        """Close the instance"""
        self.close()

    def open(self):
        self.info(f"[{self.name}] Openning the instance ...")

    def close(self):
        self.info(f"[{self.name}] Closing the instance ...")

    def __init__(self, configuration):
        super().__init__()
        self.__name = configuration.name
        self.__sources = configuration.get('sources', [])
        self.__destinations = configuration.get('destinations', [])
        self.__regles = configuration.get('regles', [])
