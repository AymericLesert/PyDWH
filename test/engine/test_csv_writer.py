# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module runs test for loading CSV file.
"""

from dotenv import load_dotenv
from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger
from connector.database.schema import DWHConnectorDatabaseSchema
from connector.engine.enginecsvwriter import DWHConnectorDatabaseEngineCSVWriter

# Charge les variables d'environnement depuis le fichier .env (dont les logins / mots de passe)

load_dotenv()

# Charge le fichier de configuration
    
configuration = DWHConfiguration("test/config/empty.yml")
schema = DWHConnectorDatabaseSchema("test")
table = schema.add("OF")
table.add("OF")
table.add("Date Heure")

# Initialise le logger

logger = DWHLogger(configuration)
logger.open()

engine = DWHConnectorDatabaseEngineCSVWriter("CSV", files = { "OF": { "filename": "D:\\024 - Team Plastique\\DWH\\OF.csv", "delimiter": "|", "encoding": "utf-8" } })
engine.open()
engine.info(engine.get_tables())
for name in engine.get_tables():
    engine.info(f"Nb rows : {engine.count_rows(name)}")
    for row in engine.get_table(name):
        engine.info(row.to_dict())
engine.close()

logger.close()