# -*- coding: utf-8 -*-

"""
This module describes a database exception on executing request.
"""

from exception.exceptiondatabase import DWHExceptionDatabase

class DWHExceptionDatabaseRequest(DWHExceptionDatabase):
    """Database exception on executing a request from the application Syncytium"""
