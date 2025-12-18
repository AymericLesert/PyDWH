# -*- coding: utf-8 -*-

"""
This module describes an exception for the application.
"""

class DWHException(Exception):
    """Basic exception"""

    @property
    def message(self):
        return self.__message

    def __init__(self, message):
        super().__init__(message)
        self.__message = message
