# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a user.
"""

class DWHUser:
    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def function(self):
        return self.__function

    def __init__(self, name, email, function = ""):
        self.__name = name
        self.__email = email
        self.__function = function