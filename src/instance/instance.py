# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the list of instances.
"""

from turtle import isvisible
from unittest.mock import seal
from exception.exceptionrule import DWHExceptionRule
from logger.loggerobject import DWHLoggerObject

from connector.database.schema import DWHConnectorDatabaseSchema
from connector.database.table import DWHConnectorDatabaseTable

from connector.reader.readermysql import DWHConnectorReaderMySQL

from connector.writer.writermysql import DWHConnectorWriterMySQL

from rule.technical.ruletechnicalignore import DWHRuleTechnicalIgnore
from rule.technical.ruletechnicalcountrow import DWHRuleTechnicalCountRow

from rule.functional.rulefunctionallistvalues import DWHRuleFunctionalListValues
from rule.functional.rulefunctionalregex import DWHRuleFunctionalRegex

class DWHInstance(DWHLoggerObject):
    @property
    def name(self):
        """Get the name of the instance"""
        return self.__name

    def __source_factory(self, name, configuration):
        self.info(f"Declaring the source '{name}' ...")

        # Get the class of the source

        try:
            klass = eval(f"DWHConnectorReader{configuration['type']}")
        except:
            self.error(f"Type '{configuration['type']}' of the source '{name}' not implemented")
            return None

        # Initiate the source

        try:
            return klass(**configuration)
        except:
            self.exception(f"Exception on declaring source '{name}'")
        
        return None

    def __table_factory(self, name, configuration):
        self.info(f"Describing the table '{name}' ...")
        return configuration.to_dict()

    def __rule_technical_factory(self, name, configuration):
        self.info(f"Defining the technical rule '{name}' ...")

        # Get the class of the source

        try:
            klass = eval(f"DWHRuleTechnical{configuration['type']}")
        except:
            self.error(f"Nature '{configuration['type']}' of the technical rule '{name}' not implemented")
            return None

        # Initiate the rule

        try:
            return klass(name, **configuration)
        except:
            self.exception(f"Exception on defining the functional rule '{name}'")

        return None

    def __rule_factory(self, name, configuration):
        self.info(f"Defining the functional rule '{name}' ...")

        # Get the class of the source

        try:
            klass = eval(f"DWHRuleFunctional{configuration['type']}")
        except:
            self.error(f"Nature '{configuration['type']}' of the rule '{name}' not implemented")
            return None

        # Initiate the rule

        try:
            return klass(**configuration)
        except:
            self.exception(f"Exception on defining the functional rule '{name}'")

        return None

    def __target_factory(self, name, configuration):
        # Initializing the target schema

        self.info(f"Initializing the schema to the target '{name}' ...")
        schema = DWHConnectorDatabaseSchema(configuration.get('database', name))

        # Building the writer

        self.info(f"Declaring the target '{name}' ...")
        connector = None

        # Get the class of the source

        try:
            klass = eval(f"DWHConnectorWriter{configuration['type']}")
        except:
            self.error(f"Type '{configuration['type']}' of the target '{name}' not implemented")
            return None

        # Initiate the source

        try:
            connector = klass(schema = schema, **configuration)
        except:
            self.exception(f"Exception on declaring target '{name}'")
            return None

        # Building the schema to the target

        self.info(f"Building the schema of the target '{name}' ...")

        for table_cfg in configuration.get('tables', []):
            # Creating the table into the schema

            table_name = table_cfg.get('name', '')
            self.info(f"Adding table '{table_name}' to the target schema ...")

            table = schema.add(DWHConnectorDatabaseTable(connector, table_name))
            table.from_tables = table_cfg.get('from', [])

            # Defining the structure of the table

            for field_name, field_cfg in table_cfg.to_dict().get('fields', {}).items():
                # Creating the field into the table
                try:
                    self.info(f"Adding field '{field_name}' ...")
                    field = table.add(name = field_name, **field_cfg)
                    if field is not None:
                        field.from_fields = field_cfg.get('from', [field_name])
                except:
                    self.exception(f"Unable to add field '{field_name}'")
            
            # Set the keys

            key_to_remove = [name for name in table_cfg.get('keys', table.fields.keys()) if name not in table.fields]
            if len(key_to_remove) > 0:
                self.warning("List of keys not described into the configuration :")
                for name in key_to_remove:
                    self.warning(f"- '{name}'")
            table.keys = [name for name in table_cfg.get('keys', table.fields.keys()) if name in table.fields]

            # TODO : Define the foreign keys

        return connector

    def __enter__(self):
        """Open a new instance"""
        self.open()
        return self

    def open(self):
        self.info("Openning the instance ...")
        
        for source in self.__sources:
            try:
                source.open()
            except:
                self.exception("Exception on openning source")

        for target in self.__targets:
            try:
                target.open()
            except:
                self.exception("Exception on openning target")

        self.__reports = {}

    @property
    def schema(self):
        """Get the schema of the instance from configuration items"""

        if self.__schema is not None:
            return self.__schema

        # Build the schema from the sources

        self.info("Building schema from sources ...")
        self.__schema = DWHConnectorDatabaseSchema(self.name)
        
        for source in self.__sources:
            self.info(f"Exracting schema from '{source.name}' ...")
            try:
                self.__schema.append(source.schema)
            except:
                self.exception(f"Exception on extracting schema '{source.name}'")

        self.info(f"Schema contains {self.__schema.count_tables} tables and {self.__schema.count_fields} fields")

        # Remove all tables not described into tables configuration

        table_to_remove = [name for name in self.__schema.tables if name not in self.__tables]
        if len(table_to_remove) > 0:
            self.warning("List of tables not described into the configuration :")
            for name in table_to_remove:
                self.warning(f"- '{name}'")
                self.__schema.remove(name)

        # Indicates all tables described which doesn't exist into schema

        first = True
        for name, cfg in self.__tables.items():
            # Check if the table from configuration exists into the source

            if name not in self.__schema.tables:
                if first:
                    self.error("List of tables described into the configuration and it doesn't exist into the schema :")
                    first = False
                self.error(f"- '{name}'")
                continue

            table = self.__schema.tables[name]

            # Set the filter on table

            table.filter = cfg.get('filter', None)

            # Set the list of keys

            key_to_remove = [name for name in cfg.get('keys', []) if name not in table.fields]
            if len(key_to_remove) > 0:
                self.warning("List of keys not described into the configuration :")
                for name in key_to_remove:
                    self.warning(f"- '{name}'")
            table.keys = [name for name in cfg.get('keys', []) if name not in key_to_remove]

            # TODO : Set the list of foreigns keys

        # Check fields for existing tables ...

        fields_removed = []
        fields_unknwon = []
        for table in self.__schema.tables.values():
            fields = {}
            for name in self.__tables[table.name].get('fields', []):
                fields[name] = True

            # Remove all fields not described into tables configuration

            field_to_remove = [name for name in table.fields if name not in fields]

            if len(field_to_remove) > 0:
                for name in field_to_remove:
                    table.remove(name)
                    fields_removed.append(f"{table.name}.{name}")

            # Indicates all fields described which doesn't exist into schema

            fields_unknwon.extend([f"{table.name}.{name}" for name in fields if not name in table.fields])

            # Add extended fields

            for name in self.__tables[table.name].get('extends', []):
                try:
                    table.extend(name)
                except:
                    self.exception(f"Unable to add an extended field '{table.name}.{name}'")

        if len(fields_removed) > 0:
            self.warning("List of fields not described into the configuration :")
            for name in fields_removed:
                self.warning(f"- '{name}'")

        if len(fields_unknwon) > 0:
            self.error("List of fields described into the configuration and it doesn't exist into the schema :")
            for name in fields_unknwon:
                self.error(f"- '{name}'")

        return self.__schema

    def update(self):
        self.verbose(f"Updating the instance ...")

        for target in self.__targets:
            try:
                target.update()
            except:
                self.exception(f"Exception on updating record to target '{target.name}'")

    def analyze(self, table_name):
        if table_name not in self.__tables:
            return False

        self.info(f"Analyzing table '{table_name}' ...")

        table = self.__schema.tables[table_name]

        # TODO : check keys

        self.info("Checking keys ...")

        # TODO : check foreigns keys

        self.info("Checking foreign keys ...")

        # apply rules on table and stop if one rule fails or has to be ignored

        self.info("Checking rules ...")

        table_cfg = self.__tables[table_name]
        for rule_name, rule in table_cfg.get('rules', {}).items():
            self.info(f"Executing rule '{rule_name}' on the table '{table_name}' ...")
            new_rule = self.__rule_technical_factory(rule_name, rule)
            if new_rule is None:
                return False

            if not new_rule.execute(table):
                return False

        return True

    def apply(self, record):
        valid = True

        for rule in self.__rules:
            try:
                rule.execute(record)
            except DWHExceptionRule as exception_rule:
                if exception_rule.name not in self.__reports:
                    self.__reports[exception_rule.name] = []
                self.__reports[exception_rule.name].append(exception_rule)
                valid = False
            except:
                self.exception(f"Exception on executing the rule '{rule.name}'")
                valid = False

        return valid

    def write(self, record):
        self.verbose(f"Writing the record '{record.to_dict()}' ...")

        for target in self.__targets:
            try:
                target.write(record)
            except:
                self.exception(f"Exception on writing record to target '{target.name}'")

    def commit(self):
        self.info(f"Committing all updated records ...")

        for target in self.__targets:
            try:
                target.commit()
            except:
                self.exception(f"Exception on committing record to target '{target.name}'")

    def reports(self):
        for name, exceptions in self.__reports.items():
            self.error(f"{name} not expected")
            for exception in exceptions:
                self.error(f"- {exception.record}")

    def close(self):
        self.info("Closing the instance ...")

        for target in reversed(self.__targets):
            try:
                target.close()
            except:
                self.exception("Exception on closing target")
        
        for source in reversed(self.__sources):
            try:
                source.close()
            except Exception as exc:
                self.exception("Exception on closing source")

    def __exit__(self, *args):
        """Close the instance"""
        self.close()

    def __init__(self, configuration):
        self.__name = configuration.get('name', '')
        super().__init__(self.name)

        # Initialisation des propriétés de l'instance

        self.__schema = None
        self.__sources = []
        self.__tables = {}
        self.__rules = []
        self.__targets = []
        self.__reports = {}

        # Creation des sources

        self.info("Declaring sources ...")
        for configuration_source in configuration.get('sources', []):
            name = configuration_source.get('name', '')
            new_source = self.__source_factory(name, configuration_source)
            if new_source is None:
                continue
            self.__sources.append(new_source)

        # Déclaration des tables

        self.info("Describing tables ...")
        for configuration_table in configuration.get('tables', []):
            name = configuration_table.get('name', '')
            new_table = self.__table_factory(name, configuration_table)
            if new_table is None:
                continue
            self.__tables[name] = new_table

        # Déclaration des règles métiers

        self.info("Describing rules ...")
        for configuration_rule in configuration.get('rules', []):
            name = configuration_rule.get('name', '')
            new_rule = self.__rule_factory(name, configuration_rule)
            if new_rule is None:
                continue
            self.__rules.append(new_rule)

        # Creation des destinations

        self.info("Declaring targets ...")
        for configuration_target in configuration.get('targets', []):
            name = configuration_target.get('name', '')
            new_target = self.__target_factory(name, configuration_target)
            if new_target is None:
                continue
            self.__targets.append(new_target)

