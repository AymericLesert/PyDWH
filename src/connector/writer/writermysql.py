# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

import mysql.connector

from tools.date import Date

from connector.database.table import DWHConnectorDatabaseTable

from connector.writer.writer import DWHConnectorWriter

from connector.engine.engine import DWHConnectorDatabaseEngine
from connector.engine.enginemysql import DWHConnectorDatabaseEngineMySQL

class DWHConnectorWriterMySQL(DWHConnectorWriter):
    @property
    def description(self):
        """Get the description of the target"""
        return super().description

    def open(self):
        """Connect to the target"""
        super().open()
        self.__engine.open()

    def update(self):
        # Create tables if not exists and alter tables if the structure has changed
        super().update(self.__engine)

    def _write(self, table):
        """Write the record into the target"""

        ids, rows = table.rows

        # TODO : Look for an existing record by its key
        # - If the key exists, update record (if somtehing changes)
        # - If the key doesn't exist, create record

        list_fields = ', '.join([f"`{field}`" for field in table.fields])
        list_values = ', '.join(["%s" for _ in table.fields])

        request = f"INSERT INTO `{table.name}` (`DWHDateHeure`, `DWHAction`, {list_fields}) VALUES (%s, %s, {list_values})"

        cursor = self.__engine.execute(request, [[Date.NOW, DWHConnectorDatabaseEngine.DWH_ACTION_ADD] + row for row in rows])
        self.__engine.commit()
        cursor.close()

        self.verbose(f"{len(rows)} records inserted into table '{table.name}'")

    def commit(self):
        super().commit()
        # TODO

    def close(self):
        """Close the connexion to the target"""
        self.__engine.close()
        super().close()

    def __init__(self, name, host = "localhost", port = 3306, user = "", password = "", database = "", schema = None, **kwargs):
        super().__init__(name, schema = schema)
        self.__engine = DWHConnectorDatabaseEngineMySQL(name,
                                                        host = host,
                                                        port = port,
                                                        user = user,
                                                        password = password,
                                                        database = database)
