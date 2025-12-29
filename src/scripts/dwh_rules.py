# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
import datetime
from dotenv import load_dotenv

from tools.date import Date
from tools.smtp import MailSender
from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger
from instance.instance import DWHInstance

def execute():
    parser = argparse.ArgumentParser(description="Run rules towards DataWareHouse")
    parser.add_argument('--config', type=str, required=True, help="Configuration file")
    parser.add_argument('--instance', type=str, required=False, help="Instance name")
    args = parser.parse_args()

    Date.NOW = datetime.datetime.now()

    # Load environment variables from the file .env

    load_dotenv()

    # Load configuration file
    
    configuration = DWHConfiguration(args.config)

    # Initialize logger

    logger = DWHLogger(configuration)
    logger.open()

    # Initialize sender mailer if needed

    mailer = None
    if configuration.get("smtp", {}).get('enable', False):
        smtp_config = configuration.smtp
        mailer = MailSender(**smtp_config)
        mailer.info("Initializing SMTP mailer ...")

    # Execute all instances

    for item in configuration.get('instances', []):
        if args.instance is not None and item.get('name', '') != args.instance:
            continue

        with DWHInstance(item, mailer) as instance:

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

    logger.close()

if __name__ == "__main__":
    execute()
