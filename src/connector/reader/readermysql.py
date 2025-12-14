# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Reader.
"""

from connector.reader.reader import DWHConnectorReader
from connector.engine.enginemysql import DWHConnectorDatabaseEngineMySQL

class DWHConnectorReaderMySQL(DWHConnectorReader):
    def open(self):
        """Connect to the source"""
        super().open()
        self.__engine.open()

    @property
    def schema(self):
        """Get the schema of the source"""

        schema = super().schema
        for name in self.__engine.get_tables():
            schema.add(self.__engine.get_table(name))

        return schema

    def count_rows(self, table_name, filter = None):
        # table_name is a name of an existing table ... by design (no risk of injection from configuration file)
        return self.__engine.count_rows(table_name, filter)

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        return self.__engine.read(table)

    def close(self):
        """Close the connexion to the source"""
        self.__engine.close()
        super().close()

    def __init__(self, name, host = "localhost", port = 3306, user = "", password = "", database = "", **kwargs):
        super().__init__(name)
        self.__engine = DWHConnectorDatabaseEngineMySQL(name,
                                                        host = host,
                                                        port = port,
                                                        user = user,
                                                        password = password,
                                                        database = database)