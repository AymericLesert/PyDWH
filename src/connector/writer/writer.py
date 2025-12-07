# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the loader component.
"""

import os

from cryptography.fernet import Fernet
from connector.database.record import DWHConnectorDatabaseRecord
from logger.loggerobject import DWHLoggerObject

class DWHConnectorWriter(DWHLoggerObject):
    """This class defines an abstract writer"""

    DWH_ACTION_ADD = 1
    DWH_ACTION_UPDATE = 2
    DWH_ACTION_REMOVE = 3

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

    def __enter__(self):
        """Open a new instance of the writer"""
        self.open()

    def open(self):
        self.info(f"Openning the writer ...")

    def update(self):
        self.info(f"Updating the writer ...")

    def _write(self, record):
        """Write the record into the target (abstract)"""
        pass

    def write(self, record):
        if self.__schema is None or record is None:
            return

        # Write the record into the target

        from_table = record.get_table().name

        for table in self.__schema.tables.values():
            if from_table not in table.from_tables:
                continue

            new_record = DWHConnectorDatabaseRecord(table)
            for field in table.fields.values():
                value = field.default_value

                for from_field in field.from_fields.get(from_table, []):
                    if from_field in record.get_table().fields.keys():
                        value = record[from_field]
                        break

                new_record[field.name] = field.convert(value)

            self._write(new_record)

    def close(self):
        self.info(f"Closing the writer ...")

    def __exit__(self, *args):
        """Close the instance of the writer"""
        self.close()

    def __init__(self, name, schema = None):
        super().__init__(name)
        self.__name = name
        self.__schema = schema
