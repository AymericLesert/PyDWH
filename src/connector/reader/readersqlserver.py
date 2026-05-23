# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginesqlserver import DWHConnectorDatabaseEngineSQLServer

class DWHConnectorReaderSQLServer(DWHConnectorReader):
    def __init__(self, name, host = "localhost", string = "", user = "", password = "", database = "", **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineSQLServer(name,
                                                                   host = host,
                                                                   string = string,
                                                                   user = user,
                                                                   password = password,
                                                                   database = database))