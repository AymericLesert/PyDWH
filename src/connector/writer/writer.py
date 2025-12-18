# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the loader component.
"""

import os

from cryptography.fernet import Fernet
from logger.loggerobject import DWHLoggerObject

from connector.database.field import DWHConnectorDatabaseField

from connector.database.record import DWHConnectorDatabaseRecord

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

    def update(self, engine):
        self.info(f"Updating the writer ...")

        #  Retrieve the list of tables into the database

        existing_tables = engine.get_tables()
        self.info(existing_tables)

        # Create the standard DWH tables

        if "DWHAction" not in existing_tables:
            engine.create_dwh()

        # Create tables into the schema on depends on the description from the configuration file

        for table in [table for table in self.schema.tables.values() if table.name not in existing_tables]:
            engine.create_table(table)

        # Update table into the schema on depends on the description from the configuration file if somtehing changes

        for table in [table for table in self.schema.tables.values() if table.name in existing_tables]:
            engine.update_table(table)

    def read(self, table):
        """Iterator on the table"""
        return None

    def _write(self, table):
        """Write the records from a table into the target (abstract)"""
        pass

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

    def commit(self):
        self.info(f"Committing the writer ...")

        for table in self.__schema.tables.values():
            self._write(table)
            table.clear()

    def close(self):
        self.info(f"Closing the writer ...")

    def __exit__(self, *args):
        """Close the instance of the writer"""
        self.close()

    def __init__(self, name, schema = None):
        super().__init__(name)
        self.__name = name
        self.__schema = schema
        self.__data = {}
