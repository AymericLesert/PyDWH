# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
from dotenv import load_dotenv

from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger
from instance.instance import DWHInstance

def execute():
    parser = argparse.ArgumentParser(description="Execution des règles d'enrichissement de l'entrepot")
    parser.add_argument('--config', type=str, required=True, help="Fichier de configuration")
    args = parser.parse_args()

    # Charge les variables d'environnement depuis le fichier .env (dont les logins / mots de passe)

    load_dotenv()

    # Charge le fichier de configuration
    
    configuration = DWHConfiguration(args.config)

    # Initialise le logger

    logger = DWHLogger(configuration)
    logger.open()

    for item in configuration.get('instances', []):
        with DWHInstance(item) as instance:

            # For each table, analyze contents, read, check and transform rows

            for name in instance.schema.tables.keys():
                instance.info(f"Executing rules for table '{name}' ...")

                if not instance.analyze(name):
                    continue

                # TODO : read, check and transform rows

    logger.close()

if __name__ == "__main__":
    execute()
