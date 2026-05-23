# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

from cryptography.fernet import Fernet

def execute():
    print("New key generated tocipher or decipher a password into the configuration file :")
    print(f"DWH_PASSWORD_KEY={Fernet.generate_key().decode('utf-8')}")

if __name__ == "__main__":
    execute()