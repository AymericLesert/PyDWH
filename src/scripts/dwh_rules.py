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

    # Charge les variables d'environnement depuis le fichier .env (dont les logins / mots de passe)

    load_dotenv()

    # Charge le fichier de configuration
    
    configuration = DWHConfiguration(args.config)

    # Initialise le logger

    logger = DWHLogger(configuration)
    logger.open()

    # Exécute les règles de transformation de données pour chaque instance

    # Cas d'usage 1 :
    #    1. Ouvrir un fichier CSV
    #    2. Récupérer la structure du fichier CSV
    #    3. Appliquer les règles de transformation
    #    4. Ecrire un nouveau fichier CSV avec les données transformées

    for item in configuration.get('instances', []):
        with DWHInstance(item) as instance:
            schema = instance.schema

    logger.close()

if __name__ == "__main__":
    execute()
