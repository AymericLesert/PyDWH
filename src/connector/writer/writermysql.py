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

    def read(self, table):
        """Iterator on the target (get the list of records from the table)"""
        return self.__engine.read(table)

    def _write(self, table):
        """Write the record into the target"""

        # Sort rows by ids

        new_rows = sorted(table.rows, key=lambda row: row[0])

        old_rows = [(record.to_values_keys(), record.to_values_fields(), record.get_datetime(), record.get_action()) for record in table]
        old_rows = sorted(old_rows, key=lambda row: row[0] + [row[2]])

        # Build SQL request

        list_fields = ', '.join([f"`{field}`" for field in table.keys] + [f"`{field}`" for field in table.fields if field not in table.keys])
        list_values = ', '.join(["%s" for _ in table.fields])

        request = f"INSERT INTO `{table.name}` ({list_fields}, `DWHAction`, `DWHDateHeure`) VALUES (%s, %s, {list_values})"

        # Look for an existing record by its key
        # - If the key exists, update record (if somtehing changes)
        # - If the key doesn't exist, create record

        i = 0
        j = 0
        rows = []

        nb_added = 0
        nb_updated = 0
        nb_removed = 0

        while i < len(old_rows) and j < len(new_rows):
            # Look for the last known records

            old_key = old_rows[i][0]
            while i + 1 < len(old_rows) and old_key == old_rows[i + 1][0]:
                i += 1

            # Compare the old record and the new one

            new_key = new_rows[j][0]

            if old_key == new_key:
                if old_rows[i][1] != new_rows[j][1]:
                    rows.append(new_rows[j][0] + new_rows[j][1] + [DWHConnectorDatabaseEngine.DWH_ACTION_UPDATE, Date.NOW])
                    nb_updated += 1
                elif old_rows[i][3] == DWHConnectorDatabaseEngine.DWH_ACTION_REMOVE:
                    rows.append(new_rows[j][0] + new_rows[j][1] + [DWHConnectorDatabaseEngine.DWH_ACTION_ADD, Date.NOW])
                    nb_added += 1
                i += 1
                j += 1
            elif old_key < new_key:
                if old_rows[i][3] != DWHConnectorDatabaseEngine.DWH_ACTION_REMOVE:
                    rows.append(old_rows[i][0] + old_rows[i][1] + [DWHConnectorDatabaseEngine.DWH_ACTION_REMOVE, Date.NOW])
                    nb_removed += 1
                i += 1
            else:
                rows.append(new_rows[j][0] + new_rows[j][1] + [DWHConnectorDatabaseEngine.DWH_ACTION_ADD, Date.NOW])
                nb_added += 1
                j += 1

        while i < len(old_rows):
            # Look for the last known records and remove it

            old_key = old_rows[i][0]
            while i+1 < len(old_rows) and old_key == old_rows[i+1][0]:
                i += 1

            rows.append(old_rows[i][0] + old_rows[i][1] + [DWHConnectorDatabaseEngine.DWH_ACTION_REMOVE, Date.NOW])
            nb_removed += 1
            i += 1

        while j < len(new_rows):
            # Add new rows

            new_key = new_rows[j][0]
            rows.append(new_rows[j][0] + new_rows[j][1] + [DWHConnectorDatabaseEngine.DWH_ACTION_ADD, Date.NOW])
            nb_added += 1
            j += 1

        # Insert records if something has changed

        if len(rows) > 0:
            cursor = self.__engine.execute(request, rows)
            self.__engine.commit()
            cursor.close()

        self.info(f"{len(rows)} records inserted into table '{table.name}' ({nb_added} added, {nb_updated} updated, {nb_removed} removed)")

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
