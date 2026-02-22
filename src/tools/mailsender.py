# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a class sending mail.
"""

import os
from re import I
import smtplib
import ssl
from email.message import EmailMessage

from cryptography.fernet import Fernet

from logger.loggerobject import DWHLoggerObject

class MailSender(DWHLoggerObject):
    @property
    def signature(self):
        return self.__signature

    def get_password(self, encrypted_password):
        """Decrypt and return the password"""
        if encrypted_password == "" or encrypted_password is None:
            return encrypted_password
        cipher_suite = Fernet(bytes(os.getenv("DWH_PASSWORD_KEY"), 'utf-8'))
        return cipher_suite.decrypt(bytes(encrypted_password, 'utf-8')).decode('utf-8')

    def send(self, to_addr, subject, corpus, filenames = None):
        try:
            self.verbose(f"Sending mail '{subject}' to {to_addr} ...")

            msg = EmailMessage()
            msg["From"] = self.__from_addr
            msg["To"] = self.__to_addr if self.__to_addr is not None else to_addr
            msg["Subject"] = subject
            msg.set_content(corpus)

            # Attachments

            files = []
            if isinstance(filenames, str):
                files.append(filenames)
            elif isinstance(filenames, list):
                files.extend(filenames)
            elif isinstance(filenames, tuple):
                files.extend(list(filenames))

            for filename in files:
                if not os.path.exists(filename) or not os.path.isfile(filename):
                    self.error(f"Attachment file '{filename}' not found")
                    continue

                with open(filename, "rb") as f:
                    msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=os.path.basename(filename))

            context = ssl.create_default_context()

            if self.__ssl:
                # SSL implicite (ex: port 465)
                with smtplib.SMTP_SSL(self.__server, self.__port, context=context, timeout=self.__timeout) as serveur:
                    serveur.login(self.__username, self.__password)
                    serveur.send_message(msg, from_addr=self.__from_addr, to_addrs=to_addr)
            else:
                # SMTP + STARTTLS (ex: port 587) ou SMTP en clair si use_starttls=False
                with smtplib.SMTP(self.__server, self.__port, timeout=self.__timeout) as serveur:
                    if self.__starttls:
                        serveur.ehlo()
                        serveur.starttls(context=context)
                        serveur.ehlo()
                    serveur.login(self.__username, self.__password)
                    serveur.send_message(msg, from_addr=self.__from_addr, to_addrs=to_addr)

            self.info(f"Mail '{subject}' to {to_addr} sent")
            return True
        except:
            self.exception(f"Unable to send mail '{subject}' to {to_addr}")
            return False

    def __init__(self,
                 server = "localhost",
                 port = 587,
                 username = None,
                 password = None,
                 from_addr = None,
                 to_addr = None,
                 ssl = False,
                 starttls = False,
                 timeout = 30,
                 signature = "",
                 **kwargs):
        """
        use_ssl=True    -> SMTP_SSL (SSL implicite, typiquement port 465)
        use_starttls=True -> starttls (TLS explicite, typiquement port 587)
        Note: ne pas activer use_ssl et use_starttls en meme temps.
        """
        super().__init__("smtp")
        self.__server = server
        self.__port = port
        self.__username = username
        try:
            self.__password = self.get_password(password)
        except:
            self.__password = password
        self.__ssl = ssl
        self.__starttls = starttls
        self.__timeout = timeout
        self.__from_addr = from_addr
        self.__to_addr = to_addr
        self.__signature = signature