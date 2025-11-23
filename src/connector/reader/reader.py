# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the reader component.
"""

import os

from cryptography.fernet import Fernet
from logger.loggerobject import DWHLoggerObject

class DWHConnectorReader(DWHLoggerObject):
    """This class defines an abstract reader"""

    def verbose(self, message):
        super().verbose(f"[{self.name}] {message}")

    def debug(self, message):
        super().debug(f"[{self.name}] {message}")

    def info(self, message):
        super().info(f"[{self.name}] {message}")

    def warning(self, message):
        super().warning(f"[{self.name}] {message}")

    def error(self, message):
        super().error(f"[{self.name}] {message}")

    def critical(self, message):
        super().critical(f"[{self.name}] {message}")

    def exception(self, message):
        super().exception(f"[{self.name}] {message}")

    def get_password(self, encrypted_password):
        """Decrypt and return the password"""
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        return cipher_suite.decrypt(bytes(encrypted_password, 'utf-8')).decode('utf-8')

    @property
    def name(self):
        """Get the name of the source"""
        return self.__name

    def __enter__(self):
        """Open a new instance of the reader"""
        self.open()

    def __exit__(self, *args):
        """Close the instance of the reader"""
        self.close()

    def open(self):
        self.info("Openning the reader ...")

    @property
    def schema(self):
        return None

    def close(self):
        self.info("Closing the reader ...")

    def __init__(self, name):
        super().__init__()
        self.__name = name
