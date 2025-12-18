# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginehfsql import DWHConnectorDatabaseEngineHFSQL

class DWHConnectorReaderHFSQL(DWHConnectorReader):
    def __init__(self, name, directory = "", **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineHFSQL(name, directory = directory))