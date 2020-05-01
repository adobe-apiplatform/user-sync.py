import logging
from collections import Mapping

import keyrings.cryptfile.cryptfile
import six
from keyring.errors import KeyringError
from ruamel.yaml import YAML

from user_sync.config import ConfigFileLoader, ConfigLoader
from user_sync.error import AssertionException

keyrings.cryptfile.cryptfile.CryptFileKeyring.keyring_key = "none"

import keyring

if (isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring) or
        isinstance(keyring.get_keyring(), keyring.backends.chainer.ChainerBackend)):
    keyring.set_keyring(keyrings.cryptfile.cryptfile.CryptFileKeyring())

yaml = YAML()
yaml.indent(mapping=4, sequence=4, offset=2)


# from ruamel.yaml.scalarstring import PreservedScalarString as pss
# full_config['umapi']['enterprise']['priv_key_data'] = pss(x)

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
        except Exception as e:
            if "stub received bad data" in str(e):
                raise AssertionException("Value for {0} too long for backend to store: {1}".format(identifier, str(e)))
            raise e

    def modify_credentials(self, action):
        all_credentials = {}
        for k, v in self.config_files.items():
            self.logger.debug("Analyzing: " + k)
            result = getattr(v, action)()
            if result:
                all_credentials[k] = result
        return all_credentials

    def load_configs(self, connector_type="all"):
        """
        This method will be responsible for reading all config files specified in user-sync-config.yml
        so that credential manager knows which keys and values are needed per file
        """
        root_cfg = ConfigFileLoader.load_root_config(self.root_config)
        root_cfg = ConfigFileLoader.load_root_config(self.root_config)
        console_log_level = root_cfg['logging']['console_log_level']
        if console_log_level == 'debug':
            self.logger.setLevel(logging.DEBUG)

        if connector_type in ['all', 'umapi']:
            for u in ConfigLoader.as_list(root_cfg['adobe_users']['connectors']['umapi']):
                self.config_files[u] = UmapiCredentialConfig(u)

        for c, v in root_cfg['directory_users']['connectors'].items():
            if connector_type in ['all', c]:
                self.config_files[v] = CredentialConfig.create(c, v)

    def store(self):
        return self.modify_credentials('store')

    def retrieve(self):
        return self.modify_credentials('retrieve')

    def revert(self):
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

    def modify_credentials(self, action):
        credentials = {}
        for c in self.secured_keys:
            try:
                # Try to do the action, but don't break on exception because rest of actions
                # can still be completed
                val = action(c)
                if val is not None:
                    credentials[':'.join(c)] = val
            except AssertionException as e:
                logging.getLogger().exception("\nError: {}\n".format(str(e)), exc_info=False)
        return credentials

    def store(self):
        credentials = self.modify_credentials(self.store_key)
        self.save()
        return credentials

    def revert(self):
        credentials = self.modify_credentials(self.revert_key)
        self.save()
        return credentials

    def retrieve(self):
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

    def store_key(self, key_list):
        """
        Takes a list of keys representing the path to a value in the YAML file, and constructs an identifier.
        If the key is a string and NOT in secure format, calls credential manager to set the key
        If key is already in the form 'secure:identifier', no action is taken.
        :param key_list: list of nested keys from a YAML file
        :return:
        """
        key_list = ConfigLoader.as_list(key_list)
        value = self.get_nested_key(key_list)
        if value is None:
            return
        if not self.parse_secure_key(value):
            k = self.get_qualified_identifier(key_list)
            CredentialManager.set(k, value)
            self.set_nested_key(key_list, {'secure': k})
            return k

    def retrieve_key(self, key_list):
        """
        Retrieves the value (if any) for key_list and returns the secure identifier if present
        If the key is not a secure key, returns None
        :param key_list:
        :return:
        """
        key_list = ConfigLoader.as_list(key_list)
        secure_identifier = self.parse_secure_key(self.get_nested_key(key_list))
        if secure_identifier is None:
            return
        value = CredentialManager.get(secure_identifier)
        if value is not None:
            return value
        raise AssertionException("No stored value found for identifier: {}".format(secure_identifier))

    def revert_key(self, key_list):
        stored_credential = self.retrieve_key(key_list)
        if stored_credential is not None:
            self.set_nested_key(key_list, stored_credential)
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


class LdapCredentialConfig(CredentialConfig):
    secured_keys = [['password']]


class OktaCredentialConfig(CredentialConfig):
    secured_keys = [['api_token']]


class UmapiCredentialConfig(CredentialConfig):
    secured_keys = [
        ['enterprise', 'api_key'],
        ['enterprise', 'client_secret'],
        ['enterprise', 'priv_key_pass']
    ]


class ConsoleCredentialConfig(CredentialConfig):
    secured_keys = [
        ['integration', 'api_key'],
        ['integration', 'client_secret'],
        ['integration', 'priv_key_pass']
    ]
