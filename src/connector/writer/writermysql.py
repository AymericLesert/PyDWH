# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the MySQL Writer.
"""

import mysql.connector

from tools.date import Date

from connector.database.table import DWHConnectorDatabaseTable

from connector.writer.writer import DWHConnectorWriter
from connector.reader.readermysql import DWHConnectorReaderMySQL

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

    def __execute(self, request, values = None):
        self.verbose(f"Executing request: {request}")
        if not values is None:
            self.verbose(f"   with values {values}")
        cursor = self.__connexion.cursor()
        if not values is None:
            cursor.execute(request, values)
        else:
            cursor.execute(request)
        return cursor

    def update(self):
        # Create tables if not exists and alter tables if structure changed

        super().update()

        #  Retrieve the list of tables into the database

        cursor_table = self.__execute("SHOW TABLES")
        existing_tables = [row[0] for row in cursor_table.fetchall()]
        cursor_table.close()
        self.info(existing_tables)

        # Create the standard DWH tables

        if "DWHAction" not in existing_tables:
            request = f"""CREATE TABLE `DWHAction` (
                                `Id` tinyint not null,
                                `Label` varchar(12) not null,
                                PRIMARY KEY (`Id`)
                            );"""
            self.__execute(request).close()

            request = "INSERT INTO `DWHAction` (`Id`, `Label`) VALUES (%s, %s)"
            self.__execute(request, (DWHConnectorWriter.DWH_ACTION_ADD, "Création")).close()
            self.__execute(request, (DWHConnectorWriter.DWH_ACTION_UPDATE, "Mise à jour")).close()
            self.__execute(request, (DWHConnectorWriter.DWH_ACTION_REMOVE, "Suppression")).close()
            self.__connexion.commit()

        # Create or alter the schema on depends on the description from the configuration file

        for table in self.schema.tables.values():
            if table.name not in existing_tables:
                self.info(f"Creating table '{table.name}' ...")

                # Set the list of fields

                fields = [field.to_mysql() for field in table.fields.values()]

                # Create the table

                request = f"""CREATE TABLE `{table.name}` (`DWHDateHeure` datetime DEFAULT NULL,
                                                           `DWHAction` tinyint DEFAULT NULL, 
                                                           {', '.join(fields)}, 
                                                           CONSTRAINT `fk_{table.name.lower()}_00` FOREIGN KEY (`DWHAction`) REFERENCES `DWHAction` (`Id`))"""
                self.__execute(request).close()
            else:
                self.info(f"Checking existing table '{table.name}' ...")

                # Retrieve the description of the existing table

                cursor_column = self.__execute(f"SHOW COLUMNS FROM `{table.name}`")
                existing_fields = {}
                table = DWHConnectorDatabaseTable(self, table.name)

                for column in cursor_column.fetchall():
                    # Get the type (length1, length2)

                    items = column[1].replace('(', ',').replace(')', '').split(',')

                    # Check if the type exists and assigns it to the standard type

                    if items[0] not in DWHConnectorReaderMySQL.MAP_TYPE:
                        self.error(f"Type ({items[0]}) of '{table.name}.{column[0]}' not implemented !")
                        continue

                    # Add default values

                    field = table.add(name = column[0], 
                                      type = DWHConnectorReaderMySQL.MAP_TYPE[items[0]], 
                                      length = items[1], 
                                      decimal = items[2], 
                                      is_null = column[2],
                                      default_value = column[4])
                    existing_fields[field.name] = field.to_mysql()

                cursor_column.close()

                # Update the schema if something changes

                self.info(f"Updating table '{table.name}' ...")

                for field in table.fields.values():
                    if field.name not in existing_fields:
                        self.info(f"Adding field '{field.name}' ...")
                        # TODO : Create a new field
                        pass
                    elif existing_fields[field.name] != field.to_mysql():
                        self.info(f"Updating field '{field.name}' ...")
                        # TODO : Update the current field
                        pass

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
