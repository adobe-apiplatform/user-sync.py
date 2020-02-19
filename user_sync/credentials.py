import logging

import keyring
from keyring.errors import KeyringError

from user_sync.error import AssertionException


class CredentialManager:
    def __init__(self):
        self.username ='user_sync'
        self.logger = logging.getLogger('credman')

    def get(self, service_name, username):
        keyring.get_password(service_name, username)

    def set(self, service_name, username, password):
        try:
            keyring.set_password(service_name, self.username, password)
            print("password stored successfully")
        except KeyringError as e:
            raise AssertionException("Error storing password ")

