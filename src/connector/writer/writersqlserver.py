# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

from connector.writer.writer import DWHConnectorWriter
from connector.engine.enginesqlserver import DWHConnectorDatabaseEngineSQLServer

class DWHConnectorWriterSQLServer(DWHConnectorWriter):
    def __init__(self, name, host = "localhost", string = "", user = "", password = "", database = "", schema = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineSQLServer(name,
                                                                   host = host,
                                                                   string = string,
                                                                   user = user,
                                                                   password = password,
                                                                   database = database),
                               schema = schema)
