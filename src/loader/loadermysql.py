# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Loader.
"""

from loader.loader import DWHLoader

class DWHLoaderMySQL(DWHLoader):
    @property
    def description(self):
        """Get the description of the source"""
        return super().description

    def open(self):
        super().open()

    def close(self):
        super().close()

    def __init__(self, *args):
        super().__init__(name)
