# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the list of instances.
"""

import os
from pickle import NONE

from exception.exceptionrule import DWHExceptionRule
from exception.exceptionrecordfieldnotfound import DWHExceptionRecordFieldNotFound

from tools.markdown import Markdown
from logger.loggerobject import DWHLoggerObject
from tools.date import Date

from users.usergroup import DWHUserGroup
from users.user import DWHUser

from connector.database.schema import DWHConnectorDatabaseSchema
from connector.database.table import DWHConnectorDatabaseTable

from connector.reader.readercsv import DWHConnectorReaderCSV
from connector.reader.readermysql import DWHConnectorReaderMySQL
from connector.reader.readersqlserver import DWHConnectorReaderSQLServer
from connector.reader.readerhfsql import DWHConnectorReaderHFSQLClassique
from connector.reader.readerhfsql import DWHConnectorReaderHFSQLClient
from connector.reader.readerpostgresql import DWHConnectorReaderPostgreSQL

from connector.writer.writercsv import DWHConnectorWriterCSV
from connector.writer.writermysql import DWHConnectorWriterMySQL
from connector.writer.writersqlserver import DWHConnectorWriterSQLServer
from connector.writer.writerspostgresql import DWHConnectorWriterPostgreSQL

from rule.technical.ruletechnicalignore import DWHRuleTechnicalIgnore
from rule.technical.ruletechnicalcountrow import DWHRuleTechnicalCountRow
from rule.technical.ruletechnicalvalues import DWHRuleTechnicalValues

from rule.functional.rulefunctionallistvalues import DWHRuleFunctionalListValues
from rule.functional.rulefunctionalregex import DWHRuleFunctionalRegex

class DWHInstance(DWHLoggerObject):
    @property
    def application(self):  
        """Get the application of the instance"""
        return self.__application

    @property
    def name(self):
        """Get the name of the instance"""
        return self.__name

    @property
    def has_error(self):
        return self.__error

    @property
    def users(self):
        """Get the list of users of the instance"""
        return self.__users

    def __user_factory(self, name, configuration):
        self.info(f"Declaring the group of users '{name}' ...")

        if configuration.get('users', None) is None:
            return DWHUserGroup(name)

        users = []
        for configuration_user in configuration.get('users').to_dict().values():
            self.verbose(f"- Adding user '{configuration_user.get('name', '')}' ...")
            users.append(DWHUser(**configuration_user))

        return DWHUserGroup(name, users)

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
            return klass(self, name, **configuration)
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
            return klass(self, **configuration)
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
            table_description = table_cfg.get('description', None)
            self.info(f"Adding table '{table_name}' to the target schema ...")

            table = schema.add(DWHConnectorDatabaseTable(connector, table_name, table_description))
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

    def send_mail(self, to_addrs, subject, content, filename = None):
        if to_addrs is None or self.application is None or self.application.mailer is None:
            self.verbose("No mail sent")
            return 0

        # Build the list of groups

        groups = []
        if isinstance(to_addrs, str):
            groups.append(to_addrs)
        elif isinstance(to_addrs, (list, tuple)):
            groups.extend(list(to_addrs))

        # Build the list of emails from groups

        users = {}
        for group in groups:
            if not group in self.users:
                continue

            for user in self.users[group].users:
                users[user.name] = user

        # Send email to all users

        nb_mails = 0
        for user in users.values():
            if self.application.mailer.send(user.email, subject, f"Bonjour {user.name},\n\n{content}\n\n{self.application.mailer.signature}", filename):
                nb_mails += 1

        self.info(f"{nb_mails} mails sent")
        return nb_mails

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

            # Set the properties of the table

            table.description = cfg.get('description', None)
            table.filter = cfg.get('filter', None)

            # Set the properties of the fields

            for field_name, field_cfg in cfg.get('fields', {}).items():
                if field_cfg is not None and field_name in table.fields:
                    table.fields[field_name].description = field_cfg.get('description', None)

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
            for name, cfg in self.__tables[table.name].get('fields', {}).items():
                fields[name] = cfg

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

        table = self.schema.tables[table_name]

        # TODO : check keys

        self.info("Checking keys ...")

        # TODO : check foreigns keys

        self.info("Checking foreign keys ...")

        # apply rules on table and stop if one rule fails or has to be ignored

        self.info("Checking rules ...")

        table_cfg = self.__tables[table_name]
        for rule_name, rule in table_cfg.get('rules', {}).items():
            self.info(f"Executing rule '{rule_name}' on the table '{table_name}' ...")
            new_rule = self.__rule_technical_factory(f"{table_name}.{rule_name}", rule)
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
            except DWHExceptionRecordFieldNotFound as exception_record:
                if exception_record.message not in self.__fields_unknown:
                    self.__fields_unknown[exception_record.message] = {}
                if rule.name not in self.__fields_unknown[exception_record.message]:
                    self.__fields_unknown[exception_record.message][rule.name] = 0
                self.__fields_unknown[exception_record.message][rule.name] += 1
                valid = False
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
        # Write all fields unknown into the log

        for name, rules in self.__fields_unknown.items():
            self.error(f"Field '{name}' unknown into the table of the source configuration")
            for rule_name, counter in rules.items():
                self.error(f"- {counter} x {rule_name}")

        if len(self.__fields_unknown) > 0 and self.__notifications['filename'] is not None:
            try:
                directory = os.path.dirname(self.__notifications['filename'])
                if directory != '':
                    try:
                        os.makedirs(directory, exist_ok=True)
                    except:
                        pass

                # Generate the technical report into a file

                self.info(f"Creating the file {self.__notifications['filename']} ...")
                with open(self.__notifications['filename'], 'w', encoding = "utf-8") as file:
                    file.write(f"---=== {Date.NOW.strftime("%Y-%m-%d")} : {self.__name} ===---\n")
                    file.write("List of fields unknown into the table of the source configuration\n")
                    for name, rules in self.__fields_unknown.items():
                        file.write(f"Field '{name}' unknown into the table of the source configuration\n")
                        for rule_name, counter in rules.items():
                            file.write(f"- {counter} x {rule_name}\n")

                # Send the report by mail

                if self.__notifications['email'] is not None:
                    self.send_mail(self.__notifications['email'], 
                                    f"[{self.name}] [{Date.NOW.strftime("%Y-%m-%d")}] Rapport technique", 
                                    "Veuillez trouver ci-joint le rapport technique.", 
                                    self.__notifications['filename'])
            except:
                self.exception("Exception on creating the technical report file")

        # Write all rules non respected into the log

        for name, exceptions in self.__reports.items():
            self.error(f"{name} not expected")

            rule = None
            for exception in exceptions:
                self.error(f"- '{exception.value}' in {exception.record}")
                rule = exception.rule

            if rule is None:
                continue

            # Generate a functional report into a file before sending the mail

            if rule.filename is not None:
                try:
                    directory = os.path.dirname(rule.filename)
                    if directory != '':
                        try:
                            os.makedirs(directory, exist_ok=True)
                        except:
                            pass

                    # Generate the function report into a file

                    self.info(f"Creating the file {rule.filename} ...")
                    with open(rule.filename, 'w', encoding = "utf-8") as file:
                        file.write(f"---=== {Date.NOW.strftime("%Y-%m-%d")} : {rule.name} - {self.__name} ===---\n")
                        file.write(f"{name} not expected\n")
                        for exception in exceptions:
                            file.write(f"- '{exception.value}' in {exception.record}\n")

                    # Send the report by mail

                    if rule.email is not None:
                        self.send_mail(rule.email, 
                                        f"[{rule.name}] [{Date.NOW.strftime("%Y-%m-%d")}] Rapport des erreurs", 
                                        f"Veuillez trouver ci-joint le rapport des erreurs du non respect :\n\n{rule.description}", 
                                        rule.filename)
                except:
                    self.exception("Exception on creating the functional report file")

    def markdown(self, directory):
        if directory is None:
            return None

        subdirectory = os.path.join(directory, self.name)
        md = Markdown(directory, os.path.join(self.name, 'home.md'))
        md.title(f"Instance {self.name}")
        if self.__description is not None:
            md.paragraph(self.__description)

        # Create sources part
            
        md.subtitle("Les sources")

        properties = []
        for source in self.__sources:
            properties.extend(source.properties)

        md.table({
                'Name': {'title': 'Nom', 'align': Markdown.CENTER},
                'Type': {'title': 'Type', 'align': Markdown.CENTER},
                'Key': {'title': 'Clé', 'align': Markdown.CENTER},
                'Properties': {'title': 'Propriétés', 'align': Markdown.LEFT},
            }, properties)

        # Create origins part
            
        md.subtitle("Les données d'origine")
        with md.bullet() as bullet:
            for table in self.schema.tables.values():
                rules = []
                table_cfg = self.__tables[table.name]

                for rule_name, rule in table_cfg.get('rules', {}).items():
                    new_rule = self.__rule_technical_factory(rule_name, rule)
                    if new_rule is None:
                        continue
                    rules.append(new_rule)

                link = os.path.join("01-Sources", table.markdown(os.path.join(subdirectory, "01-Sources"), rules))
                bullet.item(md.link(table.name, link))

        # Create transformation rules
            
        md.subtitle("Règles de transformation")
        with md.bullet() as bullet:
            for rule in self.__rules:
                link = rule.markdown(os.path.join(subdirectory, "02-Regles"))
                if link is not None:
                    bullet.item(md.link(rule.name, os.path.join("02-Regles", link)) + " : " + rule.description)
                else:
                    bullet.item(f"{rule.name} : {rule.description}")

        # Create target part
            
        md.subtitle("Les données disponibles")

        properties = []
        for target in self.__targets:
            current_properties = target.properties
            if len(current_properties) > 0 and target.schema is not None:
                property = current_properties[0]

                md_target = Markdown(subdirectory, os.path.join("03-Destinations", target.name, "home.md"))
                md_target.title(f"Liste des tables de {target.name}")
                with md_target.bullet() as bullet:
                    for table in target.schema.tables.values():
                        link = table.markdown(os.path.join(subdirectory, "03-Destinations", target.name))
                        bullet.item(md_target.link(table.name, link))
                link = md_target.close()

                for property in current_properties:
                    property['Name'] = md.link(property['Name'], link)

            properties.extend(current_properties)

        md.table({
                'Name': {'title': 'Nom', 'align': Markdown.CENTER},
                'Type': {'title': 'Type', 'align': Markdown.CENTER},
                'Key': {'title': 'Clé', 'align': Markdown.CENTER},
                'Properties': {'title': 'Propriétés', 'align': Markdown.LEFT},
            }, properties)

        return md.close()

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

    def __init__(self, application, configuration):
        self.__name = configuration.get('name', '')
        super().__init__(self.name)

        # Initialisation des propriétés de l'instance

        self.__application = application
        self.__schema = None
        self.__users = {}
        self.__sources = []
        self.__tables = {}
        self.__rules = []
        self.__targets = []
        self.__reports = {}
        self.__fields_unknown = {}
        self.__description = configuration.get('description', None)
        self.__statistics = {}
        self.__error = False
        self.__notifications = None

        # Creation des utilisateurs

        self.info("Declaring users ...")
        for configuration_users in configuration.get('users', []):
            name = configuration_users.get('name', '')
            new_group = self.__user_factory(name, configuration_users)
            if new_group is None:
                self.__error = True
                continue
            self.__users[new_group.name]= new_group

        # Creation des sources

        self.info("Declaring sources ...")
        for configuration_source in configuration.get('sources', []):
            name = configuration_source.get('name', '')
            new_source = self.__source_factory(name, configuration_source)
            if new_source is None:
                self.__error = True
                continue
            self.__sources.append(new_source)

        # Déclaration des tables

        self.info("Describing tables ...")
        for configuration_table in configuration.get('tables', []):
            name = configuration_table.get('name', '')
            new_table = self.__table_factory(name, configuration_table)
            if new_table is None:
                self.__error = True
                continue
            self.__tables[name] = new_table

        # Déclaration des règles métiers

        self.info("Describing rules ...")
        for configuration_rule in configuration.get('rules', []):
            name = configuration_rule.get('name', '')
            new_rule = self.__rule_factory(name, configuration_rule)
            if new_rule is None:
                self.__error = True
                continue
            self.__rules.append(new_rule)

        # Creation des destinations

        self.info("Declaring targets ...")
        for configuration_target in configuration.get('targets', []):
            name = configuration_target.get('name', '')
            new_target = self.__target_factory(name, configuration_target)
            if new_target is None:
                self.__error = True
                continue
            self.__targets.append(new_target)

        # TODO : Lecture des propriétés du fichier statistique

        # Destinataire des rapports techniques

        notifications = configuration.get('notifications', {})
        self.__notifications = { 'email': notifications.get('email', None), 'filename': notifications.get('filename', None) }
