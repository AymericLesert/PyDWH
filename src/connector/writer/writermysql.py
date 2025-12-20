# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

from connector.writer.writer import DWHConnectorWriter
from connector.engine.enginemysql import DWHConnectorDatabaseEngineMySQL

class DWHConnectorWriterMySQL(DWHConnectorWriter):
    def __init__(self, name, host = "localhost", port = 3306, user = "", password = "", database = "", schema = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineMySQL(name,
                                                               host = host,
                                                               port = port,
                                                               user = user,
                                                               password = password,
                                                               database = database),
                               schema = schema)
