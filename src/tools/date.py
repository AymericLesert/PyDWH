# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a class tool about the date and time.
"""

import datetime

class Date:
    DATE = "%Y-%m-%d"
    TIME = "%H:%M:%S"
    DATETIME = "%Y-%m-%d %H:%M:%S"

    NOW = datetime.datetime.now()