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

    # Exécute les règles de transformation de données pour chaque instance

    # Cas d'usage 1 :
    #    1. Ouvrir une base de données source
    #    2. Récupérer la structure (tables et champs)
    #    3. Appliquer les règles de transformation
    #    4. Ecrire un nouveau fichier CSV avec les données transformées

    for item in configuration.get('instances', []):
        with DWHInstance(item) as instance:
            # Construit le schéma de la source

            schema = instance.schema

            # Distingue les tables :
            # - les tables présentes dans le schéma sans règle de contrôle
            # - les tables présentes dans le schéma avec au moins règle de contrôle 
            # - les tables non présentes dans le schéma avec une règle de contrôle

            tables = {}
            for table in schema.tables.values():
                tables[table.name] = { 'table': table, 'technical_rules': [] }

            for technical_rule in instance.technical_rules:
                table_name = technical_rule.name
                if table_name not in tables:
                    tables[table_name] = { 'table': None, 'technical_rules': [] }
                tables[table_name]['technical_rules'].append(technical_rule)

            # Affiche le résumé des tables et règles de contrôle

            first_table = True
            for table_name, table_info in tables.items():
                if len(table_info['technical_rules']) == 0:
                    if first_table:
                        instance.warning("List of tables without technical rules :")
                        first_table = False
                    instance.warning(f"- '{table_name}'")

            first_table = True
            for table_name, table_info in tables.items():
                if table_info['table'] is None:
                    if first_table:
                        instance.error("List of check rules not concerned by the schema :")
                        first_table = False
                    instance.error(f"- '{table_name}'")

            first_table = True
            for table_name, table_info in tables.items():
                if table_info['table'] is not None and len(table_info['technical_rules']) > 0:
                    if first_table:
                        instance.info("List of technical rules to apply :")
                        first_table = False
                    instance.info(f"- '{table_name}'")

            # TODO : Applique les règles techniques

            first_table = True
            tables_to_check = []
            for table_name, table_info in tables.items():
                table = table_info['table']
                rules = table_info['technical_rules']
                if table is not None and len(rules) > 0:
                    if first_table:
                        instance.info("Applying technical rules ...")
                        first_table = False
                    instance.info(f"- '{table_name}'")

                    table_to_check = False
                    for rule in rules:
                        table.info(rule.description)
                        table_to_check = table_to_check and rule.execute(table)
                    if table_to_check:
                        tables_to_check.append(table)

            # TODO : Applique les règles de transformation sur les données de la source et écrit les résultats

    logger.close()

if __name__ == "__main__":
    execute()
