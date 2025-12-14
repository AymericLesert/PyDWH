# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract engine.
"""

import os

from cryptography.fernet import Fernet

from logger.loggerobject import DWHLoggerObject

from connector.database.table import DWHConnectorDatabaseTable

class DWHConnectorDatabaseEngine(DWHLoggerObject):
    """This class defines an abstract engine"""

    DWH_ACTION_ADD = 1
    DWH_ACTION_UPDATE = 2
    DWH_ACTION_REMOVE = 3

    @property
    def name(self):
        """Get the name of the source"""
        return self.__name

    def get_password(self, encrypted_password):
        """Decrypt and return the password"""
        if encrypted_password == "" or encrypted_password is None:
            return encrypted_password
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        return cipher_suite.decrypt(bytes(encrypted_password, 'utf-8')).decode('utf-8')

    def open(self):
        self.info("Openning the engine ...")

    def create_dwh(self):
        self.verbose("Creating DWH tables ...")

    def create_table(self, table):
        self.verbose(f"Creating table '{table.name}' ...")

    def update_table(self, table):
        self.verbose(f"Updating table '{table.name}' if something changes ...")

    def remove_table(self, table):
        self.verbose(f"Removing table '{table.name}' ...")

    def get_tables(self):
        return []

    def get_table(self, name):
        return DWHConnectorDatabaseTable(self, name)

    def read(self, table):
        return None

    def execute(self, request, values = None):
        self.verbose(f"Executing request: {request}")

        if self.isverbose and not values is None:
            self.verbose(f"   with values {values}")

    def count_rows(self, table_name, filter = None):
        return 0

    def commit(self):
        self.verbose(f"Committing ...")

    def close(self):
        self.info("Closing the engine ...")

    def __init__(self, name):
        super().__init__(name)
        self.__name = name
