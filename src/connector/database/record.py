# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from exception.exceptionrecordfieldnotfound import DWHExceptionRecordFieldNotFound

class DWHConnectorDatabaseRecord:
    """This class defines a record"""

    def __getattr__(self, field_name):
        if field_name in self.__record:
            return self.__record[field_name]

        field = self.__table.fields.get(field_name, None)
        if field is None:
            field = self.__table.extends.get(field_name, None)
        if field is None:
            return None

        return field.default_value

    def __setattr__(self, field_name, value):
        field = self.__table.fields.get(field_name, None)
        if field is None:
            field = self.__table.extends.get(field_name, None)
        if field is None:
            raise DWHExceptionRecordFieldNotFound(f"{self.__table.name}.{field_name}")

        self.__record[field_name] = field.convert(value)

    def __delattr__(self, field_name):
        if field_name in self.__record:
            del self.__record[field_name]

    def __getitem__(self, field_name):
        return self.__getattr__(field_name)

    def __setitem__(self, field_name, value):
        self.__setattr__(field_name, value)

    def __delitem__(self, field_name):
        self.__delattr__(field_name)

    def clear(self):
        """Clear the record"""
        record = self.__dict__["_DWHConnectorDatabaseRecord__record"]
        for key in list(record.keys()):
            field = self.__table.fields.get(key, None)
            if field is None:
                field = self.__table.extends.get(key, None)
            record[key] = field.default_value

    def get_table(self):
        """Get the table of the record"""
        return self.__table

    def to_dict(self):
        """Convert the record to a dictionary"""
        result = {}
        for name in self.__table.fields.keys():
            result[name] = self.__getattr__(name)
        for name in self.__table.extends.keys():
            result[name] = self.__getattr__(name)
        return result

    def __init__(self, table):
        self.__dict__["_DWHConnectorDatabaseRecord__table"] = table
        self.__dict__["_DWHConnectorDatabaseRecord__record"] = {}
