# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

from connector.writer.writer import DWHConnectorWriter
from connector.engine.enginesqlserver import DWHConnectorDatabaseEngineSQLServer

class DWHConnectorWriterSQLServer(DWHConnectorWriter):
    def get_request_insert(self, table):
        """Build SQL request"""

        list_fields = ', '.join([f"[{field}]" for field in table.keys] + [f"[{field}]" for field in table.fields if field not in table.keys])
        list_values = ', '.join(["?" for _ in table.fields])

        return f"INSERT INTO [{table.name}] ({list_fields}, [DWHAction], [DWHDateHeure]) VALUES (?, ?, {list_values})"

    def __init__(self, name, host = "localhost", string = "", user = "", password = "", database = "", schema = None, **kwargs):
        super().__init__(name, DWHConnectorDatabaseEngineSQLServer(name,
                                                                   host = host,
                                                                   string = string,
                                                                   user = user,
                                                                   password = password,
                                                                   database = database),
                               schema = schema)
