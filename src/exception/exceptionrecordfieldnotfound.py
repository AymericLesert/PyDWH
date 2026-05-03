# -*- coding: utf-8 -*-

"""
This module describes a field exception.
"""

from exception.exceptionrecordfield import DWHExceptionRecordField

class DWHExceptionRecordFieldNotFound(DWHExceptionRecordField):
    """Field not found exception into a table"""