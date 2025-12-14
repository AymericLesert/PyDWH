# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the reader component.
"""

from logger.loggerobject import DWHLoggerObject

from connector.database.schema import DWHConnectorDatabaseSchema

class DWHConnectorReader(DWHLoggerObject):
    """This class defines an abstract reader"""

    @property
    def name(self):
        """Get the name of the source"""
        return self.__name

    def __enter__(self):
        """Open a new instance of the reader"""
        self.open()

    def open(self):
        self.info("Openning the reader ...")

    @property
    def schema(self):
        return DWHConnectorDatabaseSchema(self.name)

    def count_rows(self, table_name, filter = None):
        return 0

    def close(self):
        self.info("Closing the reader ...")

    def __exit__(self, *args):
        """Close the instance of the reader"""
        self.close()

    def __init__(self, name):
        super().__init__(name)
        self.__name = name
