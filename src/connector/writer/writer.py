# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the loader component.
"""

import os

from cryptography.fernet import Fernet
from logger.loggerobject import DWHLoggerObject

class DWHConnectorWriter(DWHLoggerObject):
    """This class defines an abstract writer"""

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
        """Get the name of the target"""
        return self.__name

    @property
    def description(self):
        """Get the description of the target"""
        return { "name": self.name }

    def __enter__(self):
        """Open a new instance of the writer"""
        self.open()

    def __exit__(self, *args):
        """Close the instance of the writer"""
        self.close()

    def open(self):
        self.info(f"Openning the writer ...")

    def close(self):
        self.info(f"Closing the writer ...")

    def __init__(self, name):
        super().__init__()
        self.__name = name
