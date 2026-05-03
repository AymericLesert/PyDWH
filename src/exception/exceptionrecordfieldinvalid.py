# -*- coding: utf-8 -*-

"""
This module describes a field exception.
"""

from exception.exceptionrecordfield import DWHExceptionRecordField

class DWHExceptionRecordFieldInvalid(DWHExceptionRecordField):
    """Field invalid exception into a table"""

    @property
    def field(self):
        return self.__field

    def __init__(self, field, message):
        super().__init__(message)
        self.__field = field
