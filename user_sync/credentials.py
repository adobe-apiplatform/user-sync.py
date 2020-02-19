import logging

import keyrings.cryptfile.cryptfile
from keyring.errors import KeyringError

from user_sync.error import AssertionException

keyrings.cryptfile.cryptfile.CryptFileKeyring.keyring_key = "none"

import keyring
if (isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring) or
        isinstance(keyring.get_keyring(), keyring.backends.chainer.ChainerBackend)):
    keyring.set_keyring(keyrings.cryptfile.cryptfile.CryptFileKeyring())


class CredentialManager:

    def __init__(self):
        self.username = 'user_sync'
        self.logger = logging.getLogger("credman")
        self.keyring_name = keyring.get_keyring().name

    def get(self, identifier):
        try:
            self.logger.info("Using keyring '{0}' to retrieve '{1}'".format(self.keyring_name, identifier))
            return keyring.get_password(identifier, self.username)
        except KeyringError as e:
            raise AssertionException("Error retrieving password for identifier '{0}': {1}".format(identifier, str(e)))

    def set(self, identifier, password):
        username = 'user_sync'
        new_credential = keyring.set_password(identifier, username, password)
        return new_credential
