# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a group of users.
"""

class DWHUserGroup:
    @property
    def name(self):
        return self.__name

    @property
    def users(self):
        return self.__users

    def __init__(self, name, users = []):
        self.__name = name
        self.__users = users
