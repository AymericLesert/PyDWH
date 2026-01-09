# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module runs test for loading HF SQL.
"""

from dotenv import load_dotenv
from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger
from connector.database.schema import DWHConnectorDatabaseSchema
from connector.engine.enginehfsql import DWHConnectorDatabaseEngineHFSQL

# Charge les variables d'environnement depuis le fichier .env (dont les logins / mots de passe)

load_dotenv()

# Charge le fichier de configuration
    
configuration = DWHConfiguration("test/config/empty.yml")

# Initialise le logger

logger = DWHLogger(configuration)
logger.open()

engine = DWHConnectorDatabaseEngineHFSQL("PMINT", directory = "C:\\Mes Projets\\HF-PMINT", password = "admin")
engine.open()
engine.info(engine.get_tables())
for name in engine.get_tables():
    engine.info(f"Nb rows : {engine.count_rows(name)}")
    for row in engine.execute(f"SELECT top 10 * from {name}"):
        engine.info(row)
engine.close()

logger.close()