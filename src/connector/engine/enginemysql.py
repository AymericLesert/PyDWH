# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the engine for mysql.
"""

import mysql.connector

from connector.engine.engine import DWHConnectorDatabaseEngine
from connector.database.record import DWHConnectorDatabaseRecord

class DWHConnectorDatabaseEngineMySQL(DWHConnectorDatabaseEngine):
    """This class defines a mysql engine"""

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
        def __iter__(self):
            return self

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

            if self.__dwh:
                self.__record.set_datetime(row[i+1])
                self.__record.set_action(row[i+2])

            return self.__record

        def __init__(self, record, cursor, dwh):
            self.__record = record
            self.__cursor = cursor
            self.__dwh = dwh

    def get_request_insert(self, table):
        """Build SQL request"""

        list_fields = ', '.join([f"`{field}`" for field in table.keys] + [f"`{field}`" for field in table.fields if field not in table.keys])
        list_values = ', '.join(["%s" for _ in table.fields])

        return f"INSERT INTO `{table.name}` ({list_fields}, `DWHAction`, `DWHDateHeure`) VALUES (%s, %s, {list_values})"

    def open(self):
        """Connect to the database MySQL"""
        super().open()
        self.info(f"Connecting to MySQL database ({self.__host}.{self.__database}:{self.__port}@{self.__user})")
        try:
            self.__connexion = mysql.connector.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password, database=self.__database)
        except:
            self.exception("Connexion to MySQL database failed")
            self.__connexion = None

    def create_dwh(self):
        if self.__connexion is None:
            return

        super().create_dwh()

        request = f"""CREATE TABLE `DWHAction` (
                            `Id` tinyint not null,
                            `Label` varchar(12) not null,
                            PRIMARY KEY (`Id`)
                        );"""
        self.execute(request).close()

        request = "INSERT INTO `DWHAction` (`Id`, `Label`) VALUES (%s, %s)"
        self.execute(request, [[DWHConnectorDatabaseEngine.DWH_ACTION_ADD, "Création"], 
                               [DWHConnectorDatabaseEngine.DWH_ACTION_UPDATE, "Mise à jour"],
                               [DWHConnectorDatabaseEngine.DWH_ACTION_REMOVE, "Suppression"]]).close()
        self.commit()

    def create_table(self, table):
        if self.__connexion is None:
            return

        super().create_table(table)

        primary_key = ""
        if len(table.keys) > 0:
            primary_key = f"PRIMARY KEY (`DWHDateHeure`, {', '.join([f"`{key}`" for key in table.keys])}),"

        request = f"""CREATE TABLE `{table.name}` (`DWHDateHeure` datetime DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                                   `DWHAction` tinyint DEFAULT {DWHConnectorDatabaseEngine.DWH_ACTION_ADD} NOT NULL,
                                                   {', '.join([field.to_mysql() for field in table.fields.values()])}, 
                                                   {primary_key}
                                                   CONSTRAINT `fk_{table.name.lower()}_00` FOREIGN KEY (`DWHAction`) REFERENCES `DWHAction` (`Id`))"""
        self.execute(request).close()

    def update_table(self, table):
        if self.__connexion is None:
            return

        super().update_table(table)

        self.__dwh = True

        # Retrieve the description of the existing table

        existing_table = self.get_table(table.name)
        existing_fields = { field.name: field.to_mysql() for field in existing_table.fields.values() }

        # Update the schema if something changes

        for field in [field for field in table.fields.values() if field.name not in existing_fields]:
            self.info(f"Adding field '{field.name}' ...")
            self.execute(f"ALTER TABLE `{table.name}` ADD {field.to_mysql()}").close()

        for field in [field for field in table.fields.values() if field.name in existing_fields and existing_fields[field.name] != field.to_mysql()]:
            self.info(f"Updating field '{field.name}' ...")
            self.execute(f"ALTER TABLE `{table.name}` MODIFY COLUMN {field.to_mysql()}").close()

        # Update primary keys

        cursor_keys = self.execute(f"SHOW KEYS FROM `{table.name}` WHERE Key_name = 'PRIMARY'")
        existing_primary_key = [key[4] for key in cursor_keys]
        cursor_keys.close()

        primary_key = ['DWHDateHeure'] + table.keys
        if existing_primary_key != primary_key:
            if len(existing_primary_key) > 0:
                self.execute(f"ALTER TABLE `{table.name}` DROP PRIMARY KEY").close()
            self.execute(f"ALTER TABLE `{table.name}` ADD PRIMARY KEY ({', '.join([f"`{key}`" for key in primary_key])})").close()

    def remove_table(self, table):
        if self.__connexion is None:
            return

        super().remove_table(table)
        self.execute(f"DROP TABLE `{table.name}`").close()

    def get_tables(self):
        if self.__connexion is None:
            return []

        cursor_table = self.execute("SHOW TABLES")
        tables = [row[0] for row in cursor_table.fetchall()]
        cursor_table.close()
        return tables

    def get_table(self, name):
        if self.__connexion is None:
            return super().get_table(name)

        self.verbose(f"Describing the table '{name}' ...'")
        table = super().get_table(name)
        cursor_column = self.execute(f"SHOW COLUMNS FROM `{table.name}`")

        for column in cursor_column.fetchall():
            # Get the type (length1, length2)
            items = column[1].replace('(', ',').replace(')', '').split(',')

            # Check if the type exists and assigns it to the standard type
            if items[0] not in DWHConnectorDatabaseEngineMySQL.MAP_TYPE:
                self.error(f"Type ({items[0]}) of '{table.name}.{column[0]}' not implemented !")
                continue

            # Add default values
            items.extend([0,0])
            table.add(name = column[0], 
                        type = DWHConnectorDatabaseEngineMySQL.MAP_TYPE[items[0]], 
                        length = items[1], 
                        decimal = items[2], 
                        is_null = column[2] == 'YES',
                        default_value = column[4])

        cursor_column.close()
        return table

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        if self.__connexion is None:
            return []

        list_fields = ""
        if len(table.fields.keys()) == 0:
            list_fields = "*"
        else:
            list_fields = ', '.join([f"`{field.name}`" for field in table.fields.values() if field.type is not None])

        list_dwh = ""
        if self.__dwh:
            list_dwh = ",`DWHDateHeure`, `DWHAction`"

        if table.filter is None:
            cursor = self.execute(f"SELECT {list_fields}{list_dwh} FROM `{table.name}`")
        else:
            cursor = self.execute(f"SELECT {list_fields}{list_dwh} FROM `{table.name}` WHERE {table.filter}")

        return DWHConnectorDatabaseEngineMySQL.IteratorRecords(DWHConnectorDatabaseRecord(table), cursor, self.__dwh)

    def execute(self, request, values = None):
        if self.__connexion is None:
            return None

        super().execute(request, values)

        cursor = self.__connexion.cursor()
        if values is None:
            cursor.execute(request)
        elif (isinstance(values, list) or isinstance(values, tuple)) and (isinstance(values[0], list) or isinstance(values[0], tuple)):
            cursor.executemany(request, values)
        else:
            cursor.execute(request, values)

        return cursor

    def count_rows(self, table_name, filter = None):
        # table_name is a name of an existing table ... by design (no risk of injection from configuration file)
        if self.__connexion is None:
            return 0

        if filter is None:
            cursor_table = self.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        else:
            cursor_table = self.execute(f"SELECT COUNT(*) FROM `{table_name}` WHERE {filter}")
        count_rows = cursor_table.fetchone()[0]
        cursor_table.close()
        return count_rows

    def get_distinct_values(self, table_name, field_name, filter = None):
        if filter is None:
            cursor_table = self.execute(f"SELECT DISTINCT(`{field_name}`), COUNT(*) FROM `{table_name}` GROUP BY `{field_name}`")
        else:
            cursor_table = self.execute(f"SELECT DISTINCT(`{field_name}`), COUNT(*) FROM `{table_name}` WHERE {filter} GROUP BY `{field_name}`")

        values = cursor_table.fetchall()
        cursor_table.close()
        return values

    def rollback(self):
        super().rollback()
        if self.__connexion is not None:
            self.__connexion.rollback()

    def commit(self):
        super().commit()
        if self.__connexion is not None:
            self.__connexion.commit()

    def close(self):
        """Close the connexion to the database MySQL"""
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
        self.__dwh = False
