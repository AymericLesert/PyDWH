# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the Postgre SQL Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginepostgresql import DWHConnectorDatabaseEnginePostgreSQL

class DWHConnectorReaderPostgreSQL(DWHConnectorReader):
    def __init__(self, name, host = "localhost", port = 5432, user = "", password = "", database = "", schema_name = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEnginePostgreSQL(name,
                                                                    host = host,
                                                                    port = port,
                                                                    user = user,
                                                                    password = password,
                                                                    database = database,
                                                                    schema_name = schema_name))