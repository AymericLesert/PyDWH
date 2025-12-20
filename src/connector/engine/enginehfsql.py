# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the engine for ODBC.
"""

import win32com.client

from connector.engine.engine import DWHConnectorDatabaseEngine
from connector.database.record import DWHConnectorDatabaseRecord

class DWHConnectorDatabaseEngineHFSQL(DWHConnectorDatabaseEngine):
    """This class defines an ODBC engine"""

    MAP_TYPE = {
        200: "String",
        11: "Boolean",
        3: "Integer",
        19: "Integer",
        20: "Integer",
        4: "Double",
        135: "DateTime"
    }

    class IteratorRecords:
        def __iter__(self):
            return self

        def __next__(self):
            self.__record.clear()

            if self.__cursor.EOF:
                self.__cursor.Close()
                raise StopIteration

            table = self.__record.get_table()
            for i, field in enumerate(table.fields.values()):
                if field.type is None:
                    self.__record[field.name] = None
                else:
                    self.__record[field.name] = self.__cursor.Fields(i).Value

            self.__cursor.MoveNext()
            return self.__record

        def __init__(self, record, cursor):
            self.__record = record
            self.__cursor = cursor

    def open(self):
        """Connect to the OLE database"""
        super().open()
        self.info(f"Connecting to OLE database ({self.__directory if self.__directory is not None else self.__database})")
        try:
            self.__connexion = win32com.client.Dispatch("ADODB.Connection")

            if self.__directory is not None:
                string_connexion = f"Provider=PCSOFT.HFSQL;Initial Catalog={self.__directory};"
            elif self.__username is None:
                string_connexion = f"Provider=PCSOFT.HFSQL;Data source={self.__data_source};Initial Catalog={self.__database};"
            else:
                string_connexion = f"Provider=PCSOFT.HFSQL;Data source={self.__data_source};Initial Catalog={self.__database};" + \
                                   f"User ID={self.__username};Password={self.__password};"

            self.__connexion.Open(string_connexion)
        except:
            self.exception("Connexion to OLE database failed")
            self.__connexion = None

    def create_dwh(self):
        super().create_dwh()
        self.error("create_dwh : Not implemented!")

    def create_table(self, table):
        super().create_table(table)
        self.error("create_table : Not implemented!")

    def update_table(self, table):
        super().update_table(table)
        self.error("update_table : Not implemented!")

    def remove_table(self, table):
        super().remove_table(table)
        self.error("remove_table : Not implemented!")

    def get_tables(self):
        cursor_table = self.__connexion.OpenSchema(20)
        tables = []
        while not cursor_table.EOF:
            tables.append(cursor_table.Fields("TABLE_NAME").Value)
            cursor_table.MoveNext()
        cursor_table.Close()
        return tables

    def get_table(self, name):
        self.verbose(f"Describing the table '{name}' ...'")
        table = super().get_table(name)
        cursor_column = self.execute(f"SELECT * FROM {table.name} WHERE 1 == 0")
        if cursor_column is None:
            return table

        i = 0
        while i < cursor_column.Fields.Count:
            column_name = cursor_column.Fields(i).Name
            column_type = cursor_column.Fields(i).Type
            column_size = cursor_column.Fields(i).DefinedSize

            i += 1

            # Check if the type exists and assigns it to the standard type
            if column_type not in DWHConnectorDatabaseEngineHFSQL.MAP_TYPE:
                self.error(f"Type ({column_type}) of '{table.name}.{column_name}' not implemented !")
                continue

            # Add default values
            table.add(name = column_name, 
                      type = DWHConnectorDatabaseEngineHFSQL.MAP_TYPE[column_type],
                      length = column_size)
 
        cursor_column.Close()
        return table

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        list_fields = ""
        if len(table.fields.keys()) == 0:
            list_fields = "*"
        else:
            list_fields = ', '.join([f"{field.name}" for field in table.fields.values() if field.type is not None])

        if table.filter is None:
            cursor = self.execute(f"SELECT {list_fields} FROM {table.name}")
        else:
            cursor = self.execute(f"SELECT {list_fields} FROM {table.name} WHERE {table.filter}")

        return DWHConnectorDatabaseEngineHFSQL.IteratorRecords(DWHConnectorDatabaseRecord(table), cursor)

    def execute(self, request, values = None):
        super().execute(request, values)
        if self.__connexion is None:
            return None
        cursor = win32com.client.Dispatch("ADODB.Recordset")
        cursor.Open(request, self.__connexion, 1, 3)
        return cursor

    def count_rows(self, table_name, filter = None):
        # table_name is a name of an existing table ... by design (no risk of injection from configuration file)
        if filter is None:
            cursor_table = self.execute(f"SELECT COUNT(*) FROM {table_name}")
        else:
            cursor_table = self.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {filter}")
        count_rows = cursor_table.Fields(0).Value
        cursor_table.Close()
        return count_rows

    def rollback(self):
        super().rollback()
        self.error("rollback : Not implemented!")

    def commit(self):
        super().commit()
        self.error("commit : Not implemented!")

    def close(self):
        """Close the connexion to the OLE database"""
        if not self.__connexion is None:
            self.info("Disconnecting to OLE database")
            self.__connexion.Close()
            self.__connexion = None
        super().close()

    def __init__(self, name, directory = None, data_source = None, username = None, password = None, database = None, **kwargs):
        super().__init__(name)
        self.__directory = directory
        self.__data_source = data_source
        self.__username = username
        self.__password = self.get_password(password)
        self.__database = database
        self.__connexion = None
