# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the CSV Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginecsvreader import DWHConnectorDatabaseEngineCSVReader

class DWHConnectorReaderCSV(DWHConnectorReader):
    def __init__(self, name, files = {}, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineCSVReader(name, files = files))
