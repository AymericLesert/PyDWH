# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Reader.
"""

import mysql.connector

from connector.database.schema import DWHConnectorDatabaseSchema

from connector.reader.reader import DWHConnectorReader

class DWHConnectorReaderMySQL(DWHConnectorReader):
    def open(self):
        """Connect to the source"""
        super().open()
        self.info(f"Connecting to MySQL database ({self.__host}.{self.__database}:{self.__port}@{self.__user})")
        try:
            self.__connexion = mysql.connector.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password, database=self.__database)
        except:
            self.exception("Connexion to MySQL database failed")
            self.__connexion = None

    @property
    def schema(self):
        """Get the schema of the source"""
        schema = DWHConnectorDatabaseSchema(self.name)
        cursor_table = self.__connexion.cursor()
        cursor_table.execute("SHOW TABLES")

        for row in cursor_table.fetchall():
            table = schema.add_table(self, row[0])
            cursor_column = self.__connexion.cursor()
            cursor_column.execute(f"SHOW COLUMNS FROM `{table.name}`")
            for column in cursor_column.fetchall():
                table.add(column[0], column[1])
            cursor_column.close()

        cursor_table.close()
        return schema

    def count_rows(self, table_name, filter = None):
        # table_name is a name of an existing table ... by design (no risk of injection from configuration file)
        cursor_table = self.__connexion.cursor()
        if filter is None:
            cursor_table.execute(f"select count(*) from `{table_name}`")
        else:
            cursor_table.execute(f"select count(*) from `{table_name}` where {filter}")
        count_rows = cursor_table.fetchone()[0]
        cursor_table.close()
        return count_rows

    def close(self):
        """Close the connexion to the source"""
        if not self.__connexion is None:
            self.info("Disconnecting to MySQL database")
            self.__connexion.close()
            self.__connexion = None
        super().close()

    def __init__(self, name, host = "localhost", port = 3306, user = "", password = "", database = "", **kwargs):
        super().__init__(name)
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = self.get_password(password)
        self.__database = database
        self.__connexion = None

