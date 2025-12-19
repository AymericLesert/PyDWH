# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the engine for Postgre SQL.
"""

import mssql_python

from connector.engine.engine import DWHConnectorDatabaseEngine
from connector.database.record import DWHConnectorDatabaseRecord

from dotenv import load_dotenv
from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger

class DWHConnectorDatabaseEnginePostgreSQL(DWHConnectorDatabaseEngine):
    """This class defines a Postgre SQL engine"""

    MAP_TYPE = {
        'uniqueidentifier': 'Integer',
        'bit': 'Integer',
        'int': 'Integer',
        'bigint': 'Integer',
        'varchar': 'String',
        'nvarchar': 'String',
        'nchar': 'String',
        'char': 'String',
        'text': 'String',
        'ntext': 'String',
        'xml': 'String',
        'decimal': 'Double',
        'numeric': 'Double',
        'float': 'Double',
        'date': 'Date',
        'datetime': 'DateTime',
        'datetime2': 'DateTime',
        'varbinary': 'String'
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

    def open(self):
        """Connect to the database SQL Server"""
        super().open()
        self.info(f"Connecting to SQL Server database ({self.__host}.{self.__database}@{self.__user})")
        try:
            self.__connexion = mssql_python.connect(self.__string)
        except:
            self.exception("Connexion to SQL Server database failed")
            self.__connexion = None

    def create_dwh(self):
        super().create_dwh()

        request = "CREATE TABLE [DWHAction] ([Id] int not null PRIMARY KEY,[Label] nchar(12) not null)"
        self.execute(request).close()

        request = "INSERT INTO [DWHAction] ([Id], [Label]) VALUES (?, ?)"
        self.execute(request, [[DWHConnectorDatabaseEngine.DWH_ACTION_ADD, "Création"], 
                               [DWHConnectorDatabaseEngine.DWH_ACTION_UPDATE, "Mise à jour"],
                               [DWHConnectorDatabaseEngine.DWH_ACTION_REMOVE, "Suppression"]]).close()
        self.commit()

    def create_table(self, table):
        super().create_table(table)

        primary_key = ""
        if len(table.keys) > 0:
            primary_key = f"CONSTRAINT PK_{table.name.lower()}_Key PRIMARY KEY ([DWHDateHeure], {', '.join([f"[{key}]" for key in table.keys])}),"

        request = f"""CREATE TABLE [{table.name}] ([DWHDateHeure] datetime DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                                   [DWHAction] int DEFAULT {DWHConnectorDatabaseEngine.DWH_ACTION_ADD} NOT NULL,
                                                   {', '.join([field.to_PostgreSQL() for field in table.fields.values()])}, 
                                                   {primary_key}
                                                   CONSTRAINT FK_{table.name.lower()}_00 FOREIGN KEY ([DWHAction]) REFERENCES [DWHAction] ([Id]))"""
        self.execute(request).close()
        self.commit()

    def update_table(self, table):
        super().update_table(table)

        self.__dwh = True

        # Retrieve the description of the existing table

        existing_table = self.get_table(table.name)
        existing_fields = { field.name: field.to_PostgreSQL() for field in existing_table.fields.values() }

        # Update the schema if something changes

        for field in [field for field in table.fields.values() if field.name not in existing_fields]:
            self.info(f"Adding field '{field.name}' ...")
            self.verbose(f"Add {field.to_PostgreSQL()}")
            self.execute(f"ALTER TABLE [{table.name}] ADD {field.to_PostgreSQL()}").close()

        for field in [field for field in table.fields.values() if field.name in existing_fields and existing_fields[field.name] != field.to_PostgreSQL()]:
            self.info(f"Updating field '{field.name}' ...")
            self.verbose(f"Update from {existing_fields[field.name]} to {field.to_PostgreSQL()}")
            self.execute(f"ALTER TABLE [{table.name}] ALTER COLUMN {field.to_PostgreSQL()}").close()

        # Update primary keys

        cursor_keys = self.execute("SELECT KEY_COL.COLUMN_NAME " + \
                                   "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE as KEY_COL, INFORMATION_SCHEMA.TABLE_CONSTRAINTS as KEY_KEY "+ \
                                  f"WHERE KEY_COL.CONSTRAINT_CATALOG = '{self.__database}' " + \
                                  f"AND KEY_COL.TABLE_CATALOG = '{self.__database}' " + \
                                  f"AND KEY_COL.TABLE_NAME = '{table.name}' " + \
                                   "AND KEY_COL.CONSTRAINT_CATALOG = KEY_KEY.CONSTRAINT_CATALOG " + \
                                   "AND KEY_COL.TABLE_CATALOG = KEY_KEY.TABLE_CATALOG " + \
                                   "AND KEY_COL.TABLE_SCHEMA = KEY_KEY.TABLE_SCHEMA " + \
                                   "AND KEY_COL.TABLE_NAME = KEY_KEY.TABLE_NAME " + \
                                   "AND KEY_COL.CONSTRAINT_NAME = KEY_KEY.CONSTRAINT_NAME " + \
                                   "AND KEY_KEY.CONSTRAINT_TYPE = 'PRIMARY KEY' " + \
                                   "ORDER BY KEY_COL.ORDINAL_POSITION")

        existing_primary_key = [key[0] for key in cursor_keys]
        cursor_keys.close()

        primary_key = ['DWHDateHeure'] + table.keys
        if existing_primary_key != primary_key:
            if len(existing_primary_key) > 0:
                cursor_keys = self.execute("SELECT KEY_KEY.CONSTRAINT_NAME " + \
                                        "FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS as KEY_KEY "+ \
                                        f"WHERE KEY_KEY.CONSTRAINT_CATALOG = '{self.__database}' " + \
                                        f"AND KEY_KEY.TABLE_CATALOG = '{self.__database}' " + \
                                        f"AND KEY_KEY.TABLE_NAME = '{table.name}' " + \
                                        "AND KEY_KEY.CONSTRAINT_TYPE = 'PRIMARY KEY'")
                key_name = cursor_keys.fetchone()[0]
                self.execute(f"ALTER TABLE [{table.name}] DROP CONSTRAINT [{key_name}]").close()
                self.commit()

            self.execute(f"ALTER TABLE [{table.name}] ADD CONSTRAINT [{key_name}] PRIMARY KEY ({', '.join([f"[{key}]" for key in primary_key])})").close()
            self.commit()

    def remove_table(self, table):
        super().remove_table(table)
        self.execute(f"DROP TABLE [{table.name}]").close()
        self.commit()

    def get_tables(self):
        cursor_table = self.execute(f"SELECT TABLE_NAME " + \
                                    f"FROM INFORMATION_SCHEMA.TABLES " + \
                                    f"WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = '{self.__database}'")
        tables = [row[0] for row in cursor_table.fetchall()]
        cursor_table.close()
        return tables

    def get_table(self, name):
        self.verbose(f"Describing the table '{name}' ...'")
        table = super().get_table(name)
        cursor_column = self.execute("SELECT COLUMN_NAME,DATA_TYPE,CHARACTER_MAXIMUM_LENGTH," + \
                                             "NUMERIC_PRECISION,NUMERIC_SCALE,IS_NULLABLE,COLUMN_DEFAULT " + \
                                     "FROM INFORMATION_SCHEMA.COLUMNS " + \
                                     f"WHERE TABLE_NAME = '{table.name}' AND TABLE_CATALOG = '{self.__database}' " +\
                                     "ORDER BY ORDINAL_POSITION")

        for column in cursor_column.fetchall():
            # Check if the type exists and assigns it to the standard type
            if column[1] not in DWHConnectorDatabaseEnginePostgreSQL.MAP_TYPE:
                self.error(f"Type ({column[1]}) of '{table.name}.{column[0]}' not implemented !")
                continue

            default_value = column[6]
            if default_value is not None:
                if default_value == '(getdate())':
                    default_value = "CURRENT_TIMESTAMP"
                elif default_value.startswith('('):
                    default_value = default_value[1:-1]
                    if default_value.startswith('(') or default_value.startswith('\''):
                        default_value = default_value[1:-1]

            # Add default values
            table.add(name = column[0], 
                      type = DWHConnectorDatabaseEnginePostgreSQL.MAP_TYPE[column[1]], 
                      length = column[2] if column[2] is not None else column[3], 
                      decimal = column[4], 
                      is_null = column[5] == 'YES',
                      default_value = default_value)

        cursor_column.close()
        return table

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        list_fields = ""
        if len(table.fields.keys()) == 0:
            list_fields = "*"
        else:
            list_fields = ', '.join([f"[{field.name}]" for field in table.fields.values() if field.type is not None])

        list_dwh = ""
        if self.__dwh:
            list_dwh = ",[DWHDateHeure], [DWHAction]"

        if table.filter is None:
            cursor = self.execute(f"SELECT {list_fields}{list_dwh} FROM [{table.name}]")
        else:
            cursor = self.execute(f"SELECT {list_fields}{list_dwh} FROM [{table.name}] WHERE {table.filter}")

        return DWHConnectorDatabaseEnginePostgreSQL.IteratorRecords(DWHConnectorDatabaseRecord(table), cursor, self.__dwh)

    def execute(self, request, values = None):
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
        if filter is None:
            cursor_table = self.execute(f"SELECT COUNT(*) FROM [{table_name}]")
        else:
            cursor_table = self.execute(f"SELECT COUNT(*) FROM [{table_name}] WHERE {filter}")
        count_rows = cursor_table.fetchone()[0]
        cursor_table.close()
        return count_rows

    def commit(self):
        super().commit()
        if self.__connexion is not None:
            self.__connexion.commit()

    def close(self):
        """Close the connexion to the database SQL Server"""
        if not self.__connexion is None:
            self.info("Disconnecting to SQL Server database")
            self.__connexion.close()
            self.__connexion = None
        super().close()

    def __init__(self, name, host = "localhost", string = "", user = "", password = "", database = "", **kwargs):
        super().__init__(name)
        self.__host = host
        self.__string = string
        self.__user = user
        self.__password = self.get_password(password)
        self.__database = database
        self.__connexion = None
        self.__dwh = False

if __name__ == "__main__":

    # Charge les variables d'environnement depuis le fichier .env (dont les logins / mots de passe)

    load_dotenv()

    # Charge le fichier de configuration
    
    configuration = DWHConfiguration("../PyDWHConfig/config.yml")

    # Initialise le logger

    logger = DWHLogger(configuration)
    logger.open()

    logger.close()
