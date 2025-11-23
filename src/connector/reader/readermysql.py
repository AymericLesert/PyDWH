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
            table = schema.add_table(row[0])
            cursor_column = self.__connexion.cursor()
            cursor_column.execute(f"SHOW COLUMNS FROM `{table.name}`")
            for column in cursor_column.fetchall():
                table.add_field(column[0], column[1])
            cursor_column.close()
        cursor_table.close()
        return schema

    def close(self):
        if not self.__connexion is None:
            self.info("Disconnecting to MySQL database")
            self.__connexion.close()
            self.__connexion = None
        super().close()

    def __init__(self, name, *kargs, **kwargs):
        super().__init__(name)
        self.__host = kwargs.get("host", "localhost")
        self.__port = kwargs.get("port", 3306)
        self.__user = kwargs.get("user", "")
        self.__password = self.get_password(kwargs.get("password", ""))
        self.__database = kwargs.get("database", "")
        self.__connexion = None

