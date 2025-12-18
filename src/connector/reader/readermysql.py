# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginemysql import DWHConnectorDatabaseEngineMySQL

class DWHConnectorReaderMySQL(DWHConnectorReader):
    def __init__(self, name, host = "localhost", port = 3306, user = "", password = "", database = "", **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineMySQL(name,
                                                               host = host,
                                                               port = port,
                                                               user = user,
                                                               password = password,
                                                               database = database))