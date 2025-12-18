# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

from exception.exceptionrecordfieldnotfound import DWHExceptionRecordFieldNotFound

class DWHConnectorDatabaseRecord:
    """This class defines a record"""

    def __getattr__(self, field_name):
        record = self.__dict__["_DWHConnectorDatabaseRecord__record"]
        if field_name in record:
            return record[field_name]

        table = self.__dict__["_DWHConnectorDatabaseRecord__table"]
        field = table.fields.get(field_name, None)
        if field is None:
            field = table.extends.get(field_name, None)
        if field is None:
            return None

        return field.default_value

    def __setattr__(self, field_name, value):
        table = self.__dict__["_DWHConnectorDatabaseRecord__table"]

        field = table.fields.get(field_name, None)
        if field is None:
            field = table.extends.get(field_name, None)
        if field is None:
            raise DWHExceptionRecordFieldNotFound(f"{table.name}.{field_name}")

        self.__dict__["_DWHConnectorDatabaseRecord__record"][field_name] = field.convert(value)

    def __delattr__(self, field_name):
        record = self.__dict__["_DWHConnectorDatabaseRecord__record"]
        if field_name in record:
            del record[field_name]

    def __getitem__(self, field_name):
        return self.__getattr__(field_name)

    def __setitem__(self, field_name, value):
        self.__setattr__(field_name, value)

    def __delitem__(self, field_name):
        self.__delattr__(field_name)

    def set_datetime(self, datetime):
        self.__dict__["_DWHConnectorDatabaseRecord__datetime"] = datetime

    def get_datetime(self):
        return self.__dict__["_DWHConnectorDatabaseRecord__datetime"]

    def set_action(self, action):
        self.__dict__["_DWHConnectorDatabaseRecord__action"] = action

    def get_action(self):
        return self.__dict__["_DWHConnectorDatabaseRecord__action"]

    def clear(self):
        """Clear the record"""
        record = self.__dict__["_DWHConnectorDatabaseRecord__record"]
        table = self.__dict__["_DWHConnectorDatabaseRecord__table"]

        for key in list(record.keys()):
            field = table.fields.get(key, None)
            if field is None:
                field = table.extends.get(key, None)
            record[key] = field.default_value

    def get_table(self):
        """Get the table of the record"""
        return self.__table

    def to_dict(self):
        """Convert the record to a dictionary"""
        table = self.__dict__["_DWHConnectorDatabaseRecord__table"]
        result = {}
        for name in table.fields.keys():
            result[name] = self.__getattr__(name)
        for name in table.extends.keys():
            result[name] = self.__getattr__(name)
        return result

    def to_values_keys(self):
        """List of values included into the fields within a key"""
        return [self.__getattr__(name) for name in self.__dict__["_DWHConnectorDatabaseRecord__table"].keys]

    def to_values_fields(self):
        """List of values included into the fields without a key"""
        return [self.__getattr__(name) for name in self.__dict__["_DWHConnectorDatabaseRecord__table"].fields_no_keys]

    def __init__(self, table):
        self.__dict__["_DWHConnectorDatabaseRecord__table"] = table
        self.__dict__["_DWHConnectorDatabaseRecord__record"] = {}
        self.__dict__["_DWHConnectorDatabaseRecord__datetime"] = None
        self.__dict__["_DWHConnectorDatabaseRecord__action"] = None
