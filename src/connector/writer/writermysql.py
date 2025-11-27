# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

from connector.writer.writer import DWHConnectorWriter

class DWHConnectorWriterMySQL(DWHConnectorWriter):
    @property
    def description(self):
        """Get the description of the target"""
        return super().description

    def open(self):
        super().open()

    def close(self):
        super().close()

    def __init__(self, name, *kargs, **kwargs):
        super().__init__(name)
