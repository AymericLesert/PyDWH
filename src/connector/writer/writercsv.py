# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the CSV Writer.
"""

from connector.writer.writer import DWHConnectorWriter
from connector.engine.enginecsv import DWHConnectorDatabaseEngineCSV

class DWHConnectorWriterCSV(DWHConnectorWriter):
    def __init__(self, name, files = {}, schema = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineCSV(name, files = files), schema = schema)
