# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger
from rules.instance import DWHInstance

def execute():
    parser = argparse.ArgumentParser(description="Execution des règles d'enrichissement de l'entrepot")
    parser.add_argument('--config', type=str, required=True, help="Fichier de configuration")
    args = parser.parse_args()

    load_dotenv()
    
    configuration = DWHConfiguration(args.config)
    logger = DWHLogger(configuration)
    logger.open()
    for item in configuration.get('instances', []):
        with DWHInstance(item):
            pass
    # TODO : Execute rules
    logger.close()

if __name__ == "__main__":
    execute()
