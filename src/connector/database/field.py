# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a field type into a schema.
"""

import datetime

from logger.loggerobject import DWHLoggerObject

class DWHConnectorDatabaseField(DWHLoggerObject):
    """This class defines a field"""

    ALL_TABLES = "*"

    @property
    def table(self):
        """Get the table of the field"""
        return self.__table

    @property
    def name(self):
        """Get the name of the field"""
        return self.__name

    @property
    def description(self):
        """Get the description of the field"""
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    @property
    def format(self):
        """Get the format of the field"""
        return ""

    @property
    def type(self):
        """Get the type of the field"""
        return None

    @property
    def is_null(self):
        """Get the null possible value of the field"""
        if self.__name in self.__table.keys:
            return False
        return self.__is_null

    @property
    def default_value(self):
        """Get the default value of the field"""
        return self.__default_value

    @property
    def from_fields(self):
        return self.__from_fields

    @from_fields.setter
    def from_fields(self, from_fields):
        self.__from_fields = []

        for field in from_fields:
            if '.' in field:
                table_name, field_name = field.split('.', 1)
            else:
                table_name= DWHConnectorDatabaseField.ALL_TABLES
                field_name = field
            self.__from_fields.append((table_name, field_name))

    def copy(self, table):
        return DWHConnectorDatabaseField(table,
                                         self.__name,
                                         self.__is_null,
                                         self.__default_value,
                                         self.__description)

    def convert(self, value):
        """Convert the value to the field type"""
        # TODO: improve type conversion
        return value

    def to_mysql(self, type_mysql):
        default_value = ""
        if not self.default_value is None:
            if isinstance(self.default_value, int):
                default_value = f" DEFAULT {self.default_value}"
            elif isinstance(self.default_value, bool):
                if self.default_value:
                    default_value = " DEFAULT 1"
                else:
                    default_value = " DEFAULT 0"
            elif isinstance(self.default_value, float):
                default_value = f" DEFAULT {self.default_value}"
            elif isinstance(self.default_value, datetime.datetime):
                default_value = f" DEFAULT {self.default_value}"
            else:
                default_value = f" DEFAULT '{self.default_value}'"

        not_null = ""
        if not self.is_null:
            not_null = " NOT NULL"

        return f"`{self.name}` {type_mysql}{default_value}{not_null}"

    def to_SQLServer(self, type_sqlserver):
        default_value = ""
        if not self.default_value is None:
            if isinstance(self.default_value, int):
                default_value = f" DEFAULT {self.default_value}"
            elif isinstance(self.default_value, bool):
                if self.default_value:
                    default_value = " DEFAULT 1"
                else:
                    default_value = " DEFAULT 0"
            elif isinstance(self.default_value, float):
                default_value = f" DEFAULT {self.default_value}"
            elif isinstance(self.default_value, datetime.datetime):
                default_value = f" DEFAULT {self.default_value}"
            else:
                default_value = f" DEFAULT '{self.default_value}'"

        not_null = ""
        if not self.is_null:
            not_null = " NOT NULL"

        return f"[{self.name}] {type_sqlserver}{default_value}{not_null}"

    def to_PostgreSQL(self, type_postgresql):
        default_value = ""
        if not self.default_value is None:
            if isinstance(self.default_value, int):
                default_value = f"DEFAULT {self.default_value}"
            elif isinstance(self.default_value, bool):
                if self.default_value:
                    default_value = "DEFAULT 1"
                else:
                    default_value = "DEFAULT 0"
            elif isinstance(self.default_value, float):
                default_value = f"DEFAULT {self.default_value}"
            elif isinstance(self.default_value, datetime.datetime):
                default_value = f"DEFAULT {self.default_value}"
            else:
                default_value = f"DEFAULT '{self.default_value}'"

        not_null = ""
        if not self.is_null:
            not_null = "NOT NULL"

        return [f"\"{self.name}\"", type_postgresql, default_value, not_null]

    def __init__(self, table, name, is_null, default_value, description = ""):
        super().__init__(f"{table.connector.name}.{table.name}.{name}")
        self.__table = table
        self.__name = name
        self.__description = description
        self.__is_null = is_null
        self.__default_value = default_value
        self.__from_fields = None
