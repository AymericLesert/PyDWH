# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginehfsql import DWHConnectorDatabaseEngineHFSQL

class DWHConnectorReaderHFSQLClassique(DWHConnectorReader):
    def __init__(self, name, directory = None, password = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineHFSQL(name, 
                                                               directory = directory,
                                                               password = password))

class DWHConnectorReaderHFSQLClient(DWHConnectorReader):
    def __init__(self, name, data_source = None, username = None, password = None, database = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineHFSQL(name, 
                                                               data_source = data_source,
                                                               username = username,
                                                               password = password,
                                                               database = database))