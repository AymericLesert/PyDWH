# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
import datetime
from dotenv import load_dotenv

from tools.date import Date
from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger
from instance.application import DWHApplication

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

    # Execute application

    application = DWHApplication(configuration)
    application.execute(args.instance)

    logger.close()

if __name__ == "__main__":
    execute()
