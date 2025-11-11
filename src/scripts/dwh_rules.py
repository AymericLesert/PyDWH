# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger

def execute():
    parser = argparse.ArgumentParser(description="Execution des règles d'enrichissement de l'entrepot")
    parser.add_argument('--config', type=str, required=True, help="Fichier de configuration")
    args = parser.parse_args()

    load_dotenv()
    
    logger = DWHLogger(DWHConfiguration(args.config))
    logger.open()
    # TODO : Execute rules
    logger.close()

if __name__ == "__main__":
    execute()
