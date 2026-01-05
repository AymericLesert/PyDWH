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
        def get_rows(fields):
            rows = []
            for field in fields:
                rows.append([field.name, 
                             field.type, 
                             field.description, 
                             field.format, 
                             'Oui' if field.is_null else 'Non', 
                             field.default_value, 
                             [f"{item[0]}.{item[1]}" for item in field.from_fields] if field.from_fields is not None else []])
            return rows

        if directory is None:
            return None

        md = Markdown(directory, self.name + ".md")
        md.title(f"Table {self.name}")
        if self.__description is not None:
            md.paragraph(self.__description)
            md.paragraph()

        if self.__from_tables:
            md.paragraph("Les données sont originaires des tables :")
            with md.bullet() as bullet:
                for table_name in self.__from_tables:
                    bullet.item(md.link(table_name, os.path.join("..", "..", "01-Sources", table_name + ".md")))

        # Keys

        headers = {
            "Nom": {"title": "Nom", "align": Markdown.LEFT},
            "Type": {"title": "Type", "align": Markdown.CENTER},
            "Description": {"title": "Description", "align": Markdown.LEFT},
            "Format": {"title": "Format", "align": Markdown.LEFT},
            "Null": {"title": "Null ?", "align": Markdown.CENTER},
            "Default": {"title": "Valeur par défaut", "align": Markdown.LEFT}
        }
        if self.from_tables:
            headers['From'] = {"title": "Issu de", "align": Markdown.LEFT}

        if len(self.__keys) > 0:
            md.subtitle("Liste des clés")
            md.table(headers, get_rows([field for field in self.__fields.values() if field.name in self.__keys]))

        # Fields

        if (len(self.__fields) - len(self.__keys)) > 0:
            md.subtitle("Liste des champs")
            md.table(headers, get_rows([field for field in self.__fields.values() if field.name not in self.__keys]))

        # Extends

        if len(self.__extends) > 0:
            md.subtitle("Liste des valeurs calculées")
            md.table(headers, get_rows(self.__extends.values()))

        # Technical rules

        if len(rules) > 0:
            md.subtitle("Règles appliquées")
            with md.bullet() as bullet:
                for rule in rules:
                    link = rule.markdown(self, directory)
                    if link is not None:
                        bullet.item(f"{md.link(rule.name, link)} : {rule.description}")
                    else:
                        bullet.item(f"{rule.name} : {rule.description}")

        return md.close()

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
