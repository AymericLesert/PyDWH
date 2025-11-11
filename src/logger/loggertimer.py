# -*- coding: utf-8 -*-

"""
This module handles a timer executed.
"""

import time
import threading

class DWHLoggerTimer(threading.Thread):
    """This class handles a common logger for the application"""

    @property
    def interval(self):
        """Retrieves the interval between 2 executions in seconds"""
        return self.__interval

    def run(self):
        """Execution into the thread every x seconds"""
        while self._timer_runs.is_set():
            self.__action()
            i = 0
            while i < self.__interval and self._timer_runs.is_set():
                time.sleep(1)
                i += 1

    def stop(self):
        """Stops the thread"""
        self._timer_runs.clear()

    def __init__(self, action, interval):
        self.__action= action
        self.__interval = interval
        self._timer_runs = threading.Event()
        self._timer_runs.set()
        super().__init__()
