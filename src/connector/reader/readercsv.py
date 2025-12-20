# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the CSV Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginecsv import DWHConnectorDatabaseEngineCSV

class DWHConnectorReaderCSV(DWHConnectorReader):
    def __init__(self, name, files = {}, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineCSV(name, files = files))
