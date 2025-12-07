# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

import mysql.connector

from tools.date import Date
from connector.writer.writer import DWHConnectorWriter

class DWHConnectorWriterMySQL(DWHConnectorWriter):
    @property
    def description(self):
        """Get the description of the target"""
        return super().description

    def open(self):
        """Connect to the target"""
        super().open()
        self.info(f"Connecting to MySQL database ({self.__host}.{self.__database}:{self.__port}@{self.__user})")
        try:
            self.__connexion = mysql.connector.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password, database=self.__database)
        except:
            self.exception("Connexion to MySQL database failed")
            self.__connexion = None
        super().open()

    def update(self):
        # TODO : Create tables if not exists and alter tables if structure changed
        super().update()

    def __execute(self, request, values):
        self.verbose(f"Executing request: {request}")
        self.verbose(f"   with values {values}")
        cursor = self.__connexion.cursor()
        cursor.execute(request, values)
        return cursor

    def _write(self, record):
        """Write the record into the target (abstract)"""

        # TODO : Look for an existing record by its key
        # - If the key exists, update record (if somtehing changes)
        # - If the key doesn't exist, create record

        list_fields = ', '.join([f"`{field}`" for field in record.get_table().fields.keys()])
        list_values = ', '.join(["%s" for _ in record.get_table().fields.keys()])

        request = f"INSERT INTO `{record.get_table().name}` (`DWHDateHeure`, `DWHAction`, {list_fields}) VALUES (%s, %s, {list_values})"

        values = [Date.NOW, DWHConnectorWriter.DWH_ACTION_ADD]
        values.extend([record[field_name] for field_name in record.get_table().fields.keys()])

        cursor = self.__execute(request, values)
        self.__connexion.commit()
        cursor.close()

        self.verbose(f"Record '{record.to_dict()}' into table '{record.get_table().name}' written")

    def close(self):
        """Close the connexion to the target"""
        if not self.__connexion is None:
            self.info("Disconnecting to MySQL database")
            self.__connexion.close()
            self.__connexion = None
        super().close()

    def __init__(self, name, host = "localhost", port = 3306, user = "", password = "", database = "", schema = None, **kwargs):
        super().__init__(name, schema)
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = self.get_password(password)
        self.__database = database
        self.__connexion = None
