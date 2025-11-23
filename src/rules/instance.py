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

class DWHInstance(DWHLoggerObject):
    @property
    def name(self):
        """Get the name of the instance"""
        return self.__name

    def __enter__(self):
        """Open a new instance"""
        self.open()
        return self

    def __exit__(self, *args):
        """Close the instance"""
        self.close()

    def open(self):
        self.info(f"[{self.name}] Openning the instance ...")
        
        for source in self.__sources:
            try:
                source.open()
            except Exception as exc:
                self.exception(f"Exception on openning source")

        for target in self.__targets:
            try:
                target.open()
            except Exception as exc:
                self.exception(f"Exception on openning target")

    @property
    def schema(self):
        if self.__schema is not None:
            return self.__schema

        self.info("Extracting schema")
        self.__schema = DWHConnectorDatabaseSchema(self.__name)
        
        for source in self.__sources:
            try:
                self.__schema.append(source.schema)
            except Exception as exc:
                self.exception(f"Exception on getting schema")

        if self.isverbose:
            for table_name, table in self.__schema.tables.items():
                table.verbose(f"Table")
                for field_name, field in table.fields.items():
                    field.verbose(f"Field : ({field.type})")

        return self.__schema

    def get_rows(self):
        return {}

    def apply_rules(self, row):
        return row

    def set_row(self, row):
        pass

    def close(self):
        self.info(f"[{self.name}] Closing the instance ...")

        for target in reversed(self.__targets):
            try:
                target.close()
            except Exception as exc:
                self.exception(f"Exception on closing target")
        
        for source in reversed(self.__sources):
            try:
                source.close()
            except Exception as exc:
                self.exception(f"Exception on closing source")

    def __init__(self, configuration):
        super().__init__()
        self.__name = configuration.get('name', '')

        # Creation des sources

        self.info(f"Creating sources ...")
        self.__sources = []
        for source_cfg in configuration.get('sources', []):
            for source_name in source_cfg.keys():
                self.info(f"Creating '{source_name}' ...")
                try:
                    self.__sources.append(eval(source_cfg[source_name]['class'])(source_name, **source_cfg[source_name].get('parameters', {})))
                except Exception as exc:
                    self.exception(f"Exception on creating source")

        # Creation des destinations

        self.info(f"Creating targets ...")
        self.__targets = []
        for target_cfg in configuration.get('destinations', []):
            for target_name in target_cfg.keys():
                self.info(f"Creating '{target_name}' ...")
                try:
                    self.__targets.append(eval(target_cfg[target_name]['class'])(target_name, **target_cfg[target_name].get('parameters', {})))
                except Exception as exc:
                    self.exception(f"Exception on creating source")

        # TODO : Creation des règles

        self.info(f"Creating rules ...")
        self.__rules = configuration.get('regles', [])

        self.__schema = None
