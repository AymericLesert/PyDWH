# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

from connector.writer.writer import DWHConnectorWriter
from connector.engine.enginemysql import DWHConnectorDatabaseEngineMySQL

class DWHConnectorWriterMySQL(DWHConnectorWriter):
    def get_request_insert(self, table):
        """Build SQL request"""

        list_fields = ', '.join([f"`{field}`" for field in table.keys] + [f"`{field}`" for field in table.fields if field not in table.keys])
        list_values = ', '.join(["%s" for _ in table.fields])

        return f"INSERT INTO `{table.name}` ({list_fields}, `DWHAction`, `DWHDateHeure`) VALUES (%s, %s, {list_values})"

    def __init__(self, name, host = "localhost", port = 3306, user = "", password = "", database = "", schema = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineMySQL(name,
                                                               host = host,
                                                               port = port,
                                                               user = user,
                                                               password = password,
                                                               database = database),
                               schema = schema)
