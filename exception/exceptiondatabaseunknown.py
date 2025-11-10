# -*- coding: utf-8 -*-

"""
This module describes a database exception on unknown database instance.
"""

from exception.exceptiondatabase import DWHExceptionDatabase

class DWHExceptionDatabaseUnknown(DWHExceptionDatabase):
    """Database exception on instancing a database"""
