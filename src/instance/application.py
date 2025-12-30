# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the list of instances.
"""


import os
from tools.smtp import MailSender
from logger.loggerobject import DWHLoggerObject
from instance.instance import DWHInstance

class DWHApplication(DWHLoggerObject):
    def execute(self, instance_name):
        # Initialize documentation markdown

        markdown_file = None
        if self.__markdown_homepage is not None and self.__markdown_title is not None:
            self.info(f"Creating homepage '{self.__markdown_title}' ...")

            directory = os.path.dirname(self.__markdown_homepage)
            if directory != '':
                try:
                    os.makedirs(directory, exist_ok=True)
                except:
                    self.exception(f"Unable to create directory '{directory}' for markdown homepage")

            markdown_file = open(self.__markdown_homepage, 'w', encoding='utf-8')
            markdown_file.write(f"# {self.__markdown_title}\n\n")
            if self.__markdown_description is not None:
                markdown_file.write(f"{self.__markdown_description}\n\n")
            markdown_file.write("## Instances\n\n")

        # Execute all instances

        for item in self.__configuration.get('instances', []):
            if instance_name is not None and item.get('name', '') != instance_name:
                continue

            with DWHInstance(item, self.__mailer) as instance:

                # Update tables into the target

                instance.update()

                # For each table, analyze contents, read, check and transform rows

                for name in instance.schema.tables.keys():
                    instance.info(f"Executing rules for table '{name}' ...")

                    if not instance.analyze(name):
                        continue

                    # Read all filtered records

                    for record in instance.schema.tables[name]:
                        # apply rules on record (check and transform)
                        if instance.apply(record):
                            instance.write(record)

                # Commit all records updated

                instance.commit()

                # Create reports from exceptions identified while reading, checking and transforming records
            
                instance.reports()

                # Generate documentation if needed

                if markdown_file is not None:
                    instance.markdown(os.path.dirname(self.__markdown_homepage))

        if markdown_file is not None:
            markdown_file.close()

    def __init__(self, configuration):
        super().__init__("DWH")

        # Initialisation des propriétés de l'instance

        self.__configuration = configuration
        self.__mailer = None

        self.__markdown_homepage = None
        self.__markdown_title = None
        self.__markdown_description = None

        # Initialize sender mailer if needed

        if self.__configuration.get("smtp", {}).get('enable', False):
            smtp_config = self.__configuration.smtp
            self.__mailer = MailSender(**smtp_config)
            self.info("Initializing SMTP mailer ...")

        # Initialize documentation markdown homepage if needed

        cfg_document = self.__configuration.get('document', {})
        if cfg_document.get('enable', False):
            self.info("Documentation generation is enabled ...")
            self.__markdown_homepage = cfg_document.get('filename', None)
            self.__markdown_title = cfg_document.get('title', None)
            self.__markdown_description = cfg_document.get('description', None)
            