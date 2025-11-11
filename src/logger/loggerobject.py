# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes an abstract class of logger item.
"""

import os
import time
import getpass
from functools import wraps

from .logger import DWHLogger

class DWHLoggerObject:
    """Base object describing logger functions"""

    @property
    def isverbose(self):
        """Indicates if the log file is verbose mode"""
        if DWHLogger.Instance:
            return DWHLogger.Instance.isverbose
        return False

    @property
    def isdebug(self):
        """Indicates if the log file is debug mode"""
        if DWHLogger.Instance:
            return DWHLogger.Instance.isdebug
        return False

    @property
    def user(self):
        """Retrieve the user to show in the log file"""
        return self.__user

    def set_user(self, user):
        """Set the current user name (to trace information into the log file)"""
        self.__user = user
        return self

    def verbose(self, message):
        """This function traces a verbose message into the log file"""
        if DWHLogger.Instance:
            DWHLogger.Instance.verbose(self.__user, self.__class__.__name__, __name__, message)

    def debug(self, message):
        """This function traces a debug message into the log file"""
        if DWHLogger.Instance:
            DWHLogger.Instance.debug(self.__user, self.__class__.__name__, __name__, message)

    def info(self, message):
        """This function traces an info message into the log file"""
        if DWHLogger.Instance:
            DWHLogger.Instance.info(self.__user, self.__class__.__name__, __name__, message)

    def warning(self, message):
        """This function traces a warning message into the log file"""
        if DWHLogger.Instance:
            DWHLogger.Instance.warning(self.__user, self.__class__.__name__, __name__, message)

    def error(self, message):
        """This function traces an error message into the log file"""
        if DWHLogger.Instance:
            DWHLogger.Instance.error(self.__user, self.__class__.__name__, __name__, message)

    def critical(self, message):
        """This function traces a critical message into the log file"""
        if DWHLogger.Instance:
            DWHLogger.Instance.critical(self.__user, self.__class__.__name__, __name__, message)

    def exception(self, message):
        """This function traces the current exception raised into the log file"""
        if DWHLogger.Instance:
            DWHLogger.Instance.exception(self.__user, self.__class__.__name__, __name__, message)

    def __init__(self):
        self.__user = os.getlogin()


def asyncloggerexecutiontime(func):
    """Trace the function calling and execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            username = kwargs.get("user", None)
            if username:
                username = username['sub']
            else:
                try:
                    username = os.getlogin()
                except OSError:
                    username = getpass.getuser()

            if DWHLogger.Instance:
                DWHLogger.Instance.debug(username, func.__name__, __name__, "Starting ...")
                DWHLogger.Instance.verbose(username, func.__name__, __name__, f"Execution within parameters ({args}, {kwargs})...")

            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time

            if DWHLogger.Instance:
                DWHLogger.Instance.info(username, func.__name__, __name__, f"Execution in {execution_time:.4f} seconds")

            return result
        except:
            DWHLogger.Instance.exception(username, func.__name__, __name__, "Error on executing function")
            raise
    return wrapper
