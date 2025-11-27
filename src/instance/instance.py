# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the list of instances.
"""

from turtle import isvisible
from unittest.mock import seal
from logger.loggerobject import DWHLoggerObject

from connector.database.schema import DWHConnectorDatabaseSchema

from connector.reader.readermysql import DWHConnectorReaderMySQL

from connector.writer.writermysql import DWHConnectorWriterMySQL

from rule.ruletechnicalignore import DWHRuleTechnicalIgnore

class DWHInstance(DWHLoggerObject):
    @property
    def name(self):
        """Get the name of the instance"""
        return self.__name

    def __enter__(self):
        """Open a new instance"""
        self.open()
        return self

    def open(self):
        self.info("Openning the instance ...")
        
        for source in self.__sources:
            try:
                source.open()
            except Exception as exc:
                self.exception("Exception on openning source")

        for target in self.__targets:
            try:
                target.open()
            except Exception as exc:
                self.exception("Exception on openning target")

    @property
    def schema(self):
        if self.__schema is not None:
            return self.__schema

        self.info("Extracting schema")
        self.__schema = DWHConnectorDatabaseSchema(self.name)
        
        for source in self.__sources:
            try:
                self.__schema.append(source.schema)
            except:
                self.exception("Exception on getting schema")

        self.info(f"Schema contains {self.__schema.count_tables} tables and {self.__schema.count_fields} fields")

        return self.__schema

    @property
    def technical_rules(self):
        return self.__technical_rules

    def get_rows(self):
        return {}

    def apply_rules(self, row):
        return row

    def set_row(self, row):
        pass

    def close(self):
        self.info("Closing the instance ...")

        for target in reversed(self.__targets):
            try:
                target.close()
            except Exception as exc:
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

        # Creation des sources

        self.info("Creating sources ...")
        self.__sources = []
        for source_cfg in configuration.get('sources', []):
            for source_name in source_cfg.keys():
                self.info(f"Creating '{source_name}' ...")
                try:
                    self.__sources.append(eval(source_cfg[source_name]['class'])(source_name, **source_cfg[source_name].get('parameters', {})))
                except Exception as exc:
                    self.exception("Exception on creating source")

        # Creation des destinations

        self.info("Creating targets ...")
        self.__targets = []
        for target_cfg in configuration.get('destinations', []):
            for target_name in target_cfg.keys():
                self.info(f"Creating '{target_name}' ...")
                try:
                    self.__targets.append(eval(target_cfg[target_name]['class'])(target_name, **target_cfg[target_name].get('parameters', {})))
                except Exception as exc:
                    self.exception("Exception on creating target")

        # Creation des règles techniques

        self.info("Creating technical rules ...")
        self.__technical_rules = []
        for table_cfg in configuration.get('tables', []):
            for table_name in table_cfg.keys():
                self.info(f"Creating '{table_name}' ...")
                try:
                    self.__technical_rules.append(eval(table_cfg[table_name]['class'])(table_name, **table_cfg[table_name].get('parameters', {})))
                except Exception as exc:
                    self.exception("Exception on creating technical rule")

        # TODO : Creation des règles métiers

        self.info("Creating rules ...")
        self.__rules = configuration.get('regles', [])

        self.__schema = None
