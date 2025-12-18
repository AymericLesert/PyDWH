# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def execute():
    parser = argparse.ArgumentParser(description="Encrypt a password into the configuration")
    parser.add_argument('--password', type=str, required=True, help='Password to convert')
    args = parser.parse_args()

    load_dotenv()

    if os.getenv("DWH_PASSWORD_KEY") == '':
        print("DWH_PASSWORD_KEY is missing in the environment variables")
        return

    try:
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        print("Password encrypted :", cipher_suite.encrypt(bytes(args.password, 'utf-8')).decode('utf-8'))
    except:
        print("Please, run dsh_key_new before and add the value into the .env file !")

if __name__ == "__main__":
    execute()