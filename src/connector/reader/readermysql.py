# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Reader.
"""

import mysql.connector

from connector.database.schema import DWHConnectorDatabaseSchema
from connector.database.record import DWHConnectorDatabaseRecord

from connector.reader.reader import DWHConnectorReader

class DWHConnectorReaderMySQL(DWHConnectorReader):

    MAP_TYPE = {
        'int': 'Integer',
        'varchar': 'String',
        'text': 'String',
        'blob': 'String',
        'decimal': 'Double',
        'tinyint': 'Integer',
        'bigint unsigned': 'Integer',
        'date': 'Date',
        'datetime': 'DateTime',
    }

    class IteratorRecords:
        def __next__(self):
            self.__record.clear()
            try:
                row = self.__cursor.__next__()
            except StopIteration:
                self.__cursor.close()
                raise

            table = self.__record.get_table()
            for i, field in enumerate(table.fields.values()):
                if field.type is None:
                    self.__record[field.name] = None
                else:
                    self.__record[field.name] = row[i]


            return self.__record

        def __init__(self, record, cursor):
            self.__record = record
            self.__cursor = cursor

    def __execute(self, request):
        self.verbose(f"Executing request: {request}")
        cursor = self.__connexion.cursor()
        cursor.execute(request)
        return cursor

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

        cursor_table = self.__execute("SHOW TABLES")

        for row in cursor_table.fetchall():
            table = schema.add(self, row[0])
            cursor_column = self.__execute(f"SHOW COLUMNS FROM `{table.name}`")

            for column in cursor_column.fetchall():
                # Get the type (length1, length2)
                items = column[1].replace('(', ',').replace(')', '').split(',')

                # Check if the type exists and assigns it to the standard type
                if items[0] not in DWHConnectorReaderMySQL.MAP_TYPE:
                    self.error(f"Type ({items[0]}) of '{table.name}.{column[0]}' not implemented !")
                    continue

                # Add default values
                items.extend([0,0])
                table.add(name = column[0], 
                          type = DWHConnectorReaderMySQL.MAP_TYPE[items[0]], 
                          length = items[1], 
                          decimal = items[2], 
                          is_null = column[2],
                          default_value = column[4])

            cursor_column.close()

        cursor_table.close()
        return schema

    def count_rows(self, table_name, filter = None):
        # table_name is a name of an existing table ... by design (no risk of injection from configuration file)
        if filter is None:
            cursor_table = self.__execute(f"select count(*) from `{table_name}`")
        else:
            cursor_table = self.__execute(f"select count(*) from `{table_name}` where {filter}")
        count_rows = cursor_table.fetchone()[0]
        cursor_table.close()
        return count_rows

    def iterator(self, table):
        """Iterator on the source (get the list of records from the table)"""
        list_fields = ""
        if len(table.fields.keys()) == 0:
            list_fields = "*"
        else:
            list_fields = ', '.join([f"`{field.name}`" for field in table.fields.values() if field.type is not None])

        if table.filter is None:
            cursor = self.__execute(f"select {list_fields} from `{table.name}`")
        else:
            cursor = self.__execute(f"select {list_fields} from `{table.name}` where {table.filter}")

        return DWHConnectorReaderMySQL.IteratorRecords(DWHConnectorDatabaseRecord(table), cursor)

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

