import binascii
import logging
from collections import Mapping
from os import urandom

import click
import keyrings.cryptfile.cryptfile
import six
from keyring.errors import KeyringError
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString as pss

from user_sync import encryption
from user_sync.config import ConfigFileLoader, ConfigLoader
from user_sync.error import AssertionException

keyrings.cryptfile.cryptfile.CryptFileKeyring.keyring_key = "none"

import keyring

if (isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring) or
        isinstance(keyring.get_keyring(), keyring.backends.chainer.ChainerBackend)):
    keyring.set_keyring(keyrings.cryptfile.cryptfile.CryptFileKeyring())

yaml = YAML()
yaml.indent(mapping=4, sequence=4, offset=2)


class CredentialManager:
    username = 'user_sync'
    logger = logging.getLogger("credential_manager")
    keyring_name = keyring.get_keyring().name

    def __init__(self, root_config=None, connector_type="all"):
        self.config_files = {}
        self.root_config = root_config
        if self.root_config:
            self.load_configs(connector_type)

    @classmethod
    def get(cls, identifier, username=None):
        try:
            cls.logger.debug("Using keyring '{0}' to retrieve '{1}'".format(cls.keyring_name, identifier))
            return keyring.get_password(identifier, username or cls.username)
        except KeyringError as e:
            raise AssertionException("Error retrieving value for identifier '{0}': {1}".format(identifier, str(e)))

    @classmethod
    def set(cls, identifier, value, username=None):
        try:
            cls.logger.debug("Using keyring '{0}' to set '{1}'".format(cls.keyring_name, identifier))
            keyring.set_password(identifier, username or cls.username, value)
        except KeyringError as e:
            raise AssertionException("Error in setting credentials '{0}' : {1}".format(identifier, str(e)))

    def modify_credentials(self, action, auto_encrypt=False):
        all_credentials = {}
        for k, v in self.config_files.items():
            self.logger.debug("Analyzing: " + k)
            result = getattr(v, action)(auto_encrypt=auto_encrypt)
            if result:
                all_credentials[k] = result
        return all_credentials

    def load_configs(self, connector_type="all"):
        """
        This method will be responsible for reading all config files specified in user-sync-config.yml
        so that credential manager knows which keys and values are needed per file
        """
        root_cfg = ConfigFileLoader.load_root_config(self.root_config)
        try:
            console_log_level = root_cfg['logging']['console_log_level'].upper()
            self.logger.setLevel(console_log_level)
        except KeyError as e:
            pass

        if connector_type in ['all', 'umapi']:
            for u in ConfigLoader.as_list(root_cfg['adobe_users']['connectors']['umapi']):
                self.config_files[u] = UmapiCredentialConfig(u)

        for c, v in root_cfg['directory_users']['connectors'].items():
            if connector_type in ['all', c]:
                self.config_files[v] = CredentialConfig.create(c, v)

    def store(self, auto_encrypt=False):
        return self.modify_credentials('store', auto_encrypt)

    def retrieve(self, **kwargs):
        return self.modify_credentials('retrieve')

    def revert(self, **kwargs):
        return self.modify_credentials('revert')


class CredentialConfig:
    """
    Each method (store, revert, fetch) should be written in a subclass of this class.  This will help keep
    it all organized since filenames and config is stored within.  Shared methods are get_key, load and save.
    """
    secured_keys = []

    def __init__(self, filename=None):
        # filename will be the unique identifier for each file.  This can be an absolute path - but if so we cannot
        # move the sync tool.  More to consider here....
        self.filename = filename

        # The dictionary including comments that will be updated and re-saved
        self.load()

    @classmethod
    def create(self, subclass, filename):
        name = subclass.capitalize() + "CredentialConfig"
        return globals()[name](filename)

    def modify_credentials(self, action, **kwargs):
        credentials = {}
        for k in self.secured_keys:
            try:
                # Try to do the action, but don't break on exception because rest of actions
                # can still be completed
                val = action(k)
                if val is not None:
                    credentials[':'.join(k.key_path)] = val
            except AssertionException as e:
                logging.getLogger().exception("\nError: {}\n".format(str(e)), exc_info=False)
            except Exception as e:
                if "stub received bad data" in str(e):
                    val = self.get_nested_key(k.key_path)
                    auto_encrypt = kwargs.get('auto_encrypt')
                    if auto_encrypt:
                        data, passphrase = self.encrypt(val, auto_encrypt)
                        self.set_nested_key(k.key_path, pss(data))
                    else:
                        response = click.prompt("Bad value for '{0}': '{1}'. \nPrivate key storage may not be supported"
                                                " due to character limits.\n"
                                                "Encrypt private key instead? (y/n)".format(k, str(e)))
                        if response == 'y':
                            data, passphrase = self.encrypt(val, auto_encrypt)
                            self.set_nested_key(k.key_path, pss(data))
                        else:
                            raise AssertionException("Private key will remain in plaintext, unencrypted format.")
                    self.set_nested_key(k.key_path, pss(data))
                    self.store_key(Key(['enterprise', 'priv_key_pass']), value=passphrase)
                else:
                    raise e
        return credentials

    def encrypt(self, data, auto_encrypt):
        if auto_encrypt:
            passphrase = str(binascii.b2a_hex(urandom(16)).decode())
        else:
            passphrase = click.prompt('Create password ', hide_input=True, confirmation_prompt=True)
        return encryption.encrypt(passphrase, data), passphrase;

    def store(self, **kwargs):
        credentials = self.modify_credentials(self.store_key, **kwargs)
        self.save()
        return credentials

    def revert(self, **kwargs):
        credentials = self.modify_credentials(self.revert_key)
        self.save()
        return credentials

    def retrieve(self, **kwargs):
        return self.modify_credentials(self.retrieve_key)

    def load(self):
        with open(self.filename) as file:
            self.config = yaml.load(file)

    def save(self):
        with open(self.filename, 'w') as file:
            yaml.dump(self.config, file)

    def get_qualified_identifier(self, identifier):
        """
        Just creates a unique string (absolute filename) which pre-pends the keyname
        This ensures that all keys are stored across files, even when the key names are the same
        Additionally, this makes it clear which stored keys correspond to which files (e.g., multiple umapi)
        :param identifier: list of keys
        :return: concatenated string of keys
        """
        return self.filename + ":" + ":".join(identifier)

    def store_key(self, key, value=None):
        """
        Takes a list of keys representing the path to a value in the YAML file, and constructs an identifier.
        If the key is a string and NOT in secure format, calls credential manager to set the key
        If key is already in the form 'secure:identifier', no action is taken.
        :param key: list of nested keys from a YAML file
        :param value: credential value to be stored
        :return:
        """
        value = self.get_nested_key(key.key_path) or value
        if value is None:
            return
        if not self.parse_secure_key(value):
            k = self.get_qualified_identifier(key.key_path)
            CredentialManager.set(k, value)
            self.set_nested_key(key.key_path, {'secure': k})
            return k

    def retrieve_key(self, key):
        """
        Retrieves the value (if any) for key_list and returns the secure identifier if present
        If the key is not a secure key, returns None
        :param key:
        :return:
        """
        is_block = key.is_block
        secure_identifier = self.parse_secure_key(self.get_nested_key(key.key_path))
        if secure_identifier is None:
            return
        value = CredentialManager.get(secure_identifier)
        if is_block:
            value = pss(value)
        if value is not None:
            return value
        raise AssertionException("No stored value found for identifier: {}".format(secure_identifier))

    def revert_key(self, key):
        stored_credential = self.retrieve_key(key)
        if stored_credential is not None:
            self.set_nested_key(key.key_path, stored_credential)
        return stored_credential

    @classmethod
    def parse_secure_key(self, value):
        """
        Returns the identifier for the secure key if present, or else None
        The queried key must be a string if not secured, or a properly formatted dictionary
        containing exactly one key named 'secure' whose value is the identifier in keyring.
        """
        if value is None:
            return None
        if isinstance(value, dict):
            if len(value) == 1 and 'secure' in value:
                return value['secure']
            raise AssertionException("Invalid secure key format for '{0}'. Dict should have "
                                     "exactly one key called 'secure': {1}".format(value, value))
        elif not isinstance(value, six.text_type):
            raise AssertionException("Invalid credential format for '{0}'.  "
                                     "Key must be dict or string: {1}".format(value, value))

    def get_nested_key(self, ks, d=None):
        d = d or self.config
        k, ks = ks[0], ks[1:]
        v = d.get(k)
        if not ks:
            return v
        if isinstance(v, Mapping):
            v = self.get_nested_key(ks, v)
        elif len(ks) > 0:
            raise AssertionException("Expected dict for nested key: '{0}'".format(k))
        return v

    def set_nested_key(self, ks, u, d=None):
        d = d or self.config
        k, ks = ks[0], ks[1:]
        v = d.get(k)
        if ks and isinstance(v, Mapping):
            d[k] = self.set_nested_key(ks, u, v)
        else:
            d[k] = u
        return d


class Key:
    def __init__(self, key_path, is_block=False):
        self.key_path = key_path
        self.is_block = is_block


class LdapCredentialConfig(CredentialConfig):
    secured_keys = [Key(key_path=['password'])]


class OktaCredentialConfig(CredentialConfig):
    secured_keys = [Key(key_path=['api_token'])]


class UmapiCredentialConfig(CredentialConfig):
    secured_keys = [
        Key(key_path=['enterprise', 'api_key']),
        Key(key_path=['enterprise', 'client_secret']),
        Key(key_path=['enterprise', 'priv_key_pass']),
        Key(key_path=['enterprise', 'priv_key_data'], is_block=True)
    ]


class ConsoleCredentialConfig(CredentialConfig):
    secured_keys = [
        Key(key_path=['integration', 'api_key']),
        Key(key_path=['integration', 'client_secret']),
        Key(key_path=['integration', 'priv_key_pass']),
        Key(key_path=['integration', 'priv_key_data'], is_block=True)
    ]
