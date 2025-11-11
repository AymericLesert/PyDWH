# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module handles the configuration of the current application.
"""

import inspect
import os
import yaml

from configuration.configurationitem import DWHConfigurationItem

class DWHConfiguration:
    """This class stores the configuration of the current application"""

    EMPTY = None

    @property
    def items(self):
        """
        Retrieve the root configuration evaluated items - without items securised :
        * key, ending with '*', means that this key is securised (the value doesn't show in log file)
        """
        return self.__items

    @property
    def version(self):
        """Retrieve the current version of the package"""
        return "v" + self._get_content_file("VERSION")

    @property
    def project(self):
        """Retrieve the current application name"""
        return self._get_content_file("PROJECT")

    @property
    def empty(self):
        """Retrieves an empty configuration"""
        if DWHConfiguration.EMPTY is None:
            DWHConfiguration.EMPTY = DWHConfiguration()
        return DWHConfiguration.EMPTY

    def to_dict(self):
        """Retrieve the configuration items without evaluation"""
        return self.__configuration

    def _load(self, filename, items = None, root = './'):
        """Load a yaml file and the sub files if needed"""
        if filename is not None:
            items = filename

        if isinstance(items, str):
            if not os.path.exists(root + items):
                return items
            filename = root + items
            with open(filename, 'r', encoding="utf-8") as file:
                subitems = self._load(None, yaml.safe_load(file), os.path.dirname(filename) + '/')
            if subitems is None:
                return {}
            return subitems

        if isinstance(items, list):
            newitems = []
            for value in items:
                newitems.append(self._load(None, value, root))
            return newitems

        if isinstance(items, dict):
            newitems = {}
            for key, value in items.items():
                newitems[key] = self._load(None, value, root)
            return newitems

        return items

    def _get_content_file(self, filename):
        """Load a content text file into a string"""
        module_path = os.path.dirname(inspect.getfile(self.__class__))
        if not os.path.exists(module_path + "/" + filename):
            module_path += "/.."
        if not os.path.exists(module_path + "/" + filename):
            module_path = "."
        with open(module_path + "/" + filename, encoding = "utf-8") as content_file:
            return content_file.read().strip()

    def get(self, key, default_value = None):
        """
        Retrieve a value from a key, describing a path of a value into the configuration file
        if the key doesn't exist, the default value is retrieved
        """
        return self.__items.get(key, default_value)

    def __init__(self, filename = None):
        self.__configuration = {}
        if filename is not None:
            self.__configuration = self._load(filename)
        self.__items = DWHConfigurationItem(self, self.__configuration)
