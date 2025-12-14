# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
import datetime
from dotenv import load_dotenv

from tools.date import Date
from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger
from instance.instance import DWHInstance

def execute():
    parser = argparse.ArgumentParser(description="Execution des règles d'enrichissement de l'entrepot")
    parser.add_argument('--config', type=str, required=True, help="Fichier de configuration")
    args = parser.parse_args()

    Date.NOW = datetime.datetime.now().strftime(Date.DATETIME)

    # Charge les variables d'environnement depuis le fichier .env (dont les logins / mots de passe)

    load_dotenv()

    # Charge le fichier de configuration
    
    configuration = DWHConfiguration(args.config)

    # Initialise le logger

    logger = DWHLogger(configuration)
    logger.open()

    for item in configuration.get('instances', []):
        with DWHInstance(item) as instance:

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
