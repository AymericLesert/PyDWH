# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

"""
Main program (PyDWH)
- key.new
- key.encrypt
- key.decrypt
- rules
"""

import argparse
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from configuration.configuration import DWHConfiguration
from logger.logger import DWHLogger

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execution des règles d'enrichissement de l'entrepot")
    parser.add_argument('--name', type=str, required=True, help="key.new, ")
    parser.add_argument('--password', type=str, required=False, help='Password')
    args = parser.parse_args()

    if args.name == "key.new":
        print("Key generated to encrypt and decrypt database password :")
        print("DWH_PASSWORD_KEY=", Fernet.generate_key().decode('utf-8'))
    elif args.name == "key.encrypt":
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        print("Password encrypted :", cipher_suite.encrypt(bytes(args.password, 'utf-8')).decode('utf-8'))
    elif args.name == "key.decrypt":
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        print("Password encrypted :", cipher_suite.decrypt(bytes(args.password, 'utf-8')).decode('utf-8'))
    elif args.name == "rules":
        logger = DWHLogger(DWHConfiguration('../PyDWHConfig/config.yml'))
        logger.open()
        # TODO : Execute rules
        logger.close()
