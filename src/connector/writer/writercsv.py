# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the CSV Writer.
"""

from connector.database.schema import DWHConnectorDatabaseSchema
from connector.writer.writer import DWHConnectorWriter
from connector.engine.enginecsvwriter import DWHConnectorDatabaseEngineCSVWriter

class DWHConnectorWriterCSV(DWHConnectorWriter):
    def __init__(self, name, files = {}, schema = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineCSVWriter(name, files = files, schema = schema), schema = schema)
