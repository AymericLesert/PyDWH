# -*- coding: utf-8 -*-
# pylint: disable=ungrouped-imports

from cryptography.fernet import Fernet

def execute():
    print("Clé générée pour crypter ou décrypter un mot de passe :")
    print("DWH_PASSWORD_KEY=", Fernet.generate_key().decode('utf-8'))

if __name__ == "__main__":
    execute()