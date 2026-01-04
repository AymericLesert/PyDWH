# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the loader component.
"""

import os
from pickle import MARK
from cryptography.fernet import Fernet
from logger.loggerobject import DWHLoggerObject

from tools.date import Date
from tools.markdown import Markdown

from connector.database.field import DWHConnectorDatabaseField
from connector.database.record import DWHConnectorDatabaseRecord

from connector.engine.engine import DWHConnectorDatabaseEngine

class DWHConnectorWriter(DWHLoggerObject):
    """This class defines an abstract writer"""

    def get_password(self, encrypted_password):
        """Decrypt and return the password"""
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        return cipher_suite.decrypt(bytes(encrypted_password, 'utf-8')).decode('utf-8')

    @property
    def name(self):
        """Get the name of the target"""
        return self.__name

    @property
    def description(self):
        """Get the description of the target"""
        return { "name": self.name }

    @property
    def schema(self):
        """Get the expected schema into the database"""
        return self.__schema

    def __enter__(self):
        """Open a new instance of the writer"""
        self.open()

    def open(self):
        self.info(f"Openning the writer ...")
        self.__engine.open()

    def update(self):
        self.info(f"Updating the writer ...")

        #  Retrieve the list of tables into the database

        existing_tables = self.__engine.get_tables()
        if self.isverbose:
            self.verbose("List of existing tables :")
            for name in existing_tables:
                self.verbose(f"- {name}")

        # Create the standard DWH tables

        if "DWHAction" not in existing_tables:
            self.__engine.create_dwh()

        # Create tables into the schema on depends on the description from the configuration file

        for table in [table for table in self.schema.tables.values() if table.name not in existing_tables]:
            self.__engine.create_table(table)

        # Update table into the schema on depends on the description from the configuration file if somtehing changes

        for table in [table for table in self.schema.tables.values() if table.name in existing_tables]:
            self.__engine.update_table(table)

    def read(self, table):
        """Iterator on the target (get the list of records from the table)"""
        return self.__engine.read(table)

    def write(self, record):
        if self.__schema is None or record is None:
            return

        # Store the record into the target

        from_table = record.get_table()

        for table in self.__schema.tables.values():
            if from_table.name not in table.from_tables:
                continue

            new_record = DWHConnectorDatabaseRecord(table)
            for field in table.fields.values():
                value = field.default_value

                for from_table_name, from_field_name in field.from_fields:
                    if (from_table_name == from_table.name or from_table_name == DWHConnectorDatabaseField.ALL_TABLES) and \
                       (from_field_name in from_table.fields or from_field_name in from_table.extends):
                        value = record[from_field_name]
                        break

                new_record[field.name] = field.convert(value)

            table.store(new_record)

    def rollback_table(self, table):
        pass

    def commit_table(self, table):
        # Sort rows by ids

        new_rows = sorted(table.rows, key=lambda row: row[0])

        old_rows = [(record.to_values_keys(), record.to_values_fields(), record.get_datetime(), record.get_action()) for record in table]
        old_rows = sorted(old_rows, key=lambda row: row[0] + [row[2]])

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

            if old_rows[i][3] != DWHConnectorDatabaseEngine.DWH_ACTION_REMOVE:
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
            cursor = self.__engine.execute(self.__engine.get_request_insert(table), rows)
            self.__engine.commit()
            if cursor is not None:
                cursor.close()

        self.info(f"{len(rows)} records inserted into table '{table.name}' ({nb_added} added, {nb_updated} updated, {nb_removed} removed)")

    def rollback(self):
        self.info(f"Rollbacking the writer ...")

        for table in self.__schema.tables.values():
            self.rollback_table(table)
            table.clear()

    def commit(self):
        self.info(f"Committing the writer ...")

        for table in self.__schema.tables.values():
            self.commit_table(table)
            table.clear()

    def markdown(self, markdown_file, directory, sub_directory):
        """Generate the markdown documentation for the writer"""
        link = None
        if self.__schema is not None:
            self.info(f"Creating markdown documentation for writer '{self.name}' ...")

            new_directory = os.path.join(directory, sub_directory, self.name)
            try:
                os.makedirs(new_directory, exist_ok=True)
            except:
                self.exception(f"Unable to create directory '{new_directory}' for markdown instance")

            markdown_filename = os.path.join(new_directory, "home.md")
            markdown_subfile = open(markdown_filename, 'w', encoding='utf-8')
            markdown_subfile.write(f"# Liste des tables de {self.name}\n\n")
            for table in self.__schema.tables.values():
                link = table.markdown(new_directory)
                markdown_subfile.write(f"- [{table.name}]({link})\n")
            markdown_subfile.close()
            Markdown.Convert(markdown_filename)
            link = os.path.join(sub_directory, self.name, "home.md")

        properties = self.__engine.properties

        if len(properties) == 0:
            if link is not None:
                markdown_file.write(f"| [{self.name.upper()}]({link}) | {self.__engine.type} | | |\n")
            else:
                markdown_file.write(f"| {self.name.upper()} | {self.__engine.type} | | |\n")
            return

        for key, property in properties:
            values = "<br>".join([f"{item_key}: {item_value}" for item_key, item_value in property.items()])
            if link is not None:
                markdown_file.write(f"| [{self.name.upper()}]({link}) | {self.__engine.type} | {key} | {values} |\n")
            else:
                markdown_file.write(f"| {self.name.upper()} | {self.__engine.type} | {key} | {values} |\n")

    def close(self):
        self.info(f"Closing the writer ...")
        self.__engine.close()

    def __exit__(self, *args):
        """Close the instance of the writer"""
        self.close()

    def __init__(self, name, engine, schema = None):
        super().__init__(name)
        self.__name = name
        self.__engine = engine
        self.__schema = schema
