# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def execute():
    parser = argparse.ArgumentParser(description="Cryptage d'un mot de passe")
    parser.add_argument('--password', type=str, required=True, help='Mot de passe à convertir')
    args = parser.parse_args()

    load_dotenv()

    cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
    print("Password encrypted :", cipher_suite.encrypt(bytes(args.password, 'utf-8')).decode('utf-8'))

if __name__ == "__main__":
    execute()