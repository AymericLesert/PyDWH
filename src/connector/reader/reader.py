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

    @property
    def properties(self):
        """Generate the markdown documentation for the reader"""
        properties = self.__engine.properties

        if len(properties) == 0:
            return [{
                        'Name': self.name.upper(),
                        'Type': self.__engine.type
                    }]

        values = []
        for key, property in properties:
            values.append({
                'Name': self.name.upper(),
                'Type': self.__engine.type,
                'Key': key,
                'Properties': [f"{item_key}: {item_value}" for item_key, item_value in property.items()]
            })
        return values

    def __enter__(self):
        """Open a new instance of the reader"""
        self.open()

    def open(self):
        self.info("Openning the reader ...")
        self.__engine.open()

    @property
    def schema(self):
        """Get the schema of the source"""

        schema = DWHConnectorDatabaseSchema(self.name)

        for name in self.__engine.get_tables():
            schema.add(self.__engine.get_table(name, ""))

        return schema

    def count_rows(self, table_name, filter = None):
        # table_name is a name of an existing table ... by design (no risk of injection from configuration file)
        return self.__engine.count_rows(table_name, filter)

    def read(self, table):
        """Iterator on the source (get the list of records from the table)"""
        return self.__engine.read(table)

    def close(self):
        self.info("Closing the reader ...")

    def __exit__(self, *args):
        """Close the instance of the reader"""
        self.__engine.close()
        self.close()

    def __init__(self, name, engine):
        super().__init__(name)
        self.__name = name
        self.__engine = engine
