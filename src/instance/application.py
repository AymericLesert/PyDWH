# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the list of instances.
"""


import os

from tools.smtp import MailSender
from tools.markdown import Markdown
from logger.loggerobject import DWHLoggerObject
from instance.instance import DWHInstance

class DWHApplication(DWHLoggerObject):
    def execute(self, instance_name, nodoc):
        # Initialize documentation markdown

        md = None
        bullet = None

        if (nodoc is None or nodoc == False) and self.__markdown_homepage is not None and self.__markdown_title is not None:
            md = Markdown(os.path.dirname(self.__markdown_homepage), os.path.basename(self.__markdown_homepage))
            md.title(self.__markdown_title)
            if self.__markdown_description is not None:
                md.paragraph(self.__markdown_description)
            md.subtitle("Instances")
            bullet = md.bullet()
            bullet.start()

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

                if bullet is not None:
                    link = instance.markdown(os.path.dirname(self.__markdown_homepage))
                    if link is not None:
                        bullet.item(md.link(instance.name.upper(), link))
                    

        if md is not None:
            bullet.end()
            md.close()

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
            