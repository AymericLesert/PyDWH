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

    def open(self):
        self.info("Openning the reader ...")

    @property
    def schema(self):
        return None

    def close(self):
        self.info("Closing the reader ...")

    def __exit__(self, *args):
        """Close the instance of the reader"""
        self.close()

    def __init__(self, name):
        super().__init__(name)
        self.__name = name
