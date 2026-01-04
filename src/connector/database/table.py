# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the schema structure.
"""

import os

from tools.markdown import Markdown

from logger.loggerobject import DWHLoggerObject

from connector.database.field import DWHConnectorDatabaseField
from connector.database.fieldstring import DWHConnectorDatabaseFieldString
from connector.database.fieldinteger import DWHConnectorDatabaseFieldInteger
from connector.database.fielddouble import DWHConnectorDatabaseFieldDouble
from connector.database.fieldboolean import DWHConnectorDatabaseFieldBoolean
from connector.database.fielddate import DWHConnectorDatabaseFieldDate
from connector.database.fielddatetime import DWHConnectorDatabaseFieldDateTime
from connector.database.fieldjson import DWHConnectorDatabaseFieldJSON

class DWHConnectorDatabaseTable(DWHLoggerObject):
    """This class defines a table containing Fields"""

    @property
    def connector(self):
        """Get the connector of the table"""
        return self.__connector

    @property
    def name(self):
        """Get the name of the table"""
        return self.__name

    @property
    def description(self):
        """Get the description of the table"""
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    @property
    def fields(self):
        """Get the fields of the table"""
        return self.__fields

    @property
    def extends(self):
        """Get the extended fields of the table"""
        return self.__extends

    @property
    def fields_no_keys(self):
        if self.__fields_no_keys is None:
            self.__fields_no_keys = [name for name in self.__fields if name not in self.__keys]
            self.__fields_no_keys.extend([name for name in self.__extends if name not in self.__keys])
        return self.__fields_no_keys

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, keys):
        self.__keys = keys

    @property
    def filter(self):
        return self.__filter

    @filter.setter
    def filter(self, filter):
        self.__filter = filter

    @property
    def from_tables(self):
        return self.__from_tables

    @from_tables.setter
    def from_tables(self, from_tables):
        self.__from_tables = from_tables

    @property
    def count_fields(self):
        """Get the number of fields in the table"""
        return len(self.__fields)

    def add(self, name, type = "String", length = None, decimal = None, is_null = True, default_value = None, description = "", **kwargs):
        if name not in self.__fields:
            try:
                klass = eval(f"DWHConnectorDatabaseField{type}")
            except:
                self.error(f"Type '{type}' of the field '{name}' not implemented")
                return None

            self.__fields[name] = klass(self, name = name, 
                                              length = length,
                                              decimal = decimal, 
                                              is_null = is_null,
                                              default_value = default_value,
                                              description = description)
        return self.__fields[name]

    def add_field(self, field):
        if field is None:
            return None

        if field.name not in self.__fields:
            self.__fields[field.name] = field.copy(self)

        return self.__fields[field.name]

    def extend(self, name, type = "String", length = None, decimal = None, is_null = True, default_value = None, description = "", **kwargs):
        if name not in self.__fields:
            try:
                klass = eval(f"DWHConnectorDatabaseField{type}")
            except:
                self.error(f"Type '{type}' of the field '{name}' not implemented")
                return None

            self.__extends[name] = klass(self, name = name, 
                                               length = length,
                                               decimal = decimal, 
                                               is_null = is_null,
                                               default_value = default_value,
                                               description = description)
        return self.__extends[name]

    def remove(self, field_name):
        if field_name not in self.__fields:
            return
        del self.__fields[field_name]

    @property
    def count_rows(self):
        return self.connector.count_rows(self.name, self.filter)

    def get_distinct_values(self, field_name):
        return self.connector.get_distinct_values(self.name, field_name, self.filter)

    def clear(self):
        self.__rows.clear()

    def store(self, record):
        if record is None:
            return

        self.__rows.append((record.to_values_keys(), record.to_values_fields()))

    @property
    def rows(self):
        return self.__rows

    def markdown(self, directory, rules = []):
        def write_fields(markdown_file, table, fields):
            from_fields = ""
            from_separation = ""
            if table.from_tables:
                from_fields = " Issu de |"
                from_separation = " :--- |"

            markdown_file.write(f"| Nom | Type | Description | Format | Null ? | Valeur par défaut |{from_fields}\n")
            markdown_file.write(f"| :--- | :---: | :--- | :--- | :---: | :--- |{from_separation}\n")
            for field in fields:
                from_item=""
                if table.from_tables:
                    from_item = "<br>".join([f"{item[0]}.{item[1]}" for item in field.from_fields]) + " |"
                markdown_file.write(f"| {field.name} | {field.type} | {field.description} | {field.format} | {'Oui' if field.is_null else 'Non'} | {field.default_value} |{from_item}\n")
            markdown_file.write("\n")

        if directory is None:
            return None

        self.info(f"Creating markdown documentation for table '{self.name}' ...")

        try:
            os.makedirs(directory, exist_ok=True)
        except:
            self.exception(f"Unable to create directory '{directory}' for markdown table")

        markdown_filename = os.path.join(directory, self.name + ".md")
        markdown_file = open(markdown_filename, 'w', encoding='utf-8')
        markdown_file.write(f"# Table {self.name}\n\n")
        if self.__description is not None:
            markdown_file.write(f"{self.__description}\n\n")

        if self.__from_tables:
            markdown_file.write("Les données sont originaires des tables :\n\n")
            for table_name in self.__from_tables:
                markdown_file.write(f"- [{table_name}]({os.path.join("..", "..", "01-Sources", table_name + ".md")})\n")

        # Keys

        if len(self.__keys) > 0:
            markdown_file.write("## Liste des clés\n\n")
            write_fields(markdown_file, self, [field for field in self.__fields.values() if field.name in self.__keys])

        # Fields

        if (len(self.__fields) - len(self.__keys)) > 0:
            markdown_file.write("## Liste des champs\n\n")
            write_fields(markdown_file, self, [field for field in self.__fields.values() if field.name not in self.__keys])

        # Extends

        if len(self.__extends) > 0:
            markdown_file.write("## Liste des valeurs calculées\n\n")
            write_fields(markdown_file, self, self.__extends.values())

        # Technical rules

        if len(rules) > 0:
            markdown_file.write("## Règles appliquées\n\n")
            for rule in rules:
                link = rule.markdown(self, os.path.join(directory, self.name))
                if link is not None:
                    markdown_file.write(f"- [{rule.name}]({link}) : {rule.description}\n")
                else:
                    markdown_file.write(f"- {rule.name} : {rule.description}\n")

        markdown_file.close()
        Markdown.Convert(markdown_filename)

        return self.name + ".md"

    def __iter__(self):
        """Iterator on the records from the table"""
        return self.connector.read(self)

    def __init__(self, connector, name, description):
        super().__init__(f"{connector.name}.{name}")
        self.__connector = connector
        self.__name = name
        self.__description = description
        self.__filter = None
        self.__fields = {}
        self.__extends = {}
        self.__keys = []
        self.__fields_no_keys = None

        self.__from_tables = None
        self.__rows = []
