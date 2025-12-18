# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

import argparse
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

def execute():
    parser = argparse.ArgumentParser(description="Decipher a password")
    parser.add_argument('--password', type=str, required=True, help='Password to read')
    args = parser.parse_args()

    load_dotenv()

    if os.getenv("DWH_PASSWORD_KEY") == '':
        print("DWH_PASSWORD_KEY is missing in the environment variables")
        return

    try:
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        print("Deciphered password :", cipher_suite.decrypt(args.password.encode('utf-8')).decode('utf-8'))
    except:
        print("The password is invalid ... check it!")

if __name__ == "__main__":
    execute()