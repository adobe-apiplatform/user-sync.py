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

    def __init__(self, root_config=None):

        self.config_files = {}
        self.root_config = root_config

        if self.root_config:
            self.load_configs()

        print()

    @classmethod
    def get(cls, identifier, username=None):
        try:
            cls.logger.debug("Using keyring '{0}' to retrieve '{1}'".format(cls.keyring_name, identifier))
            return keyring.get_password(identifier, username or cls.username)
        except KeyringError as e:
            raise AssertionException("Error retrieving value for identifier '{0}': {1}".format(identifier, str(e)))

    @classmethod
    def set(cls, identifier, value):
        try:
            cls.logger.debug("Using keyring '{0}' to set '{1}'".format(cls.keyring_name, identifier))
            keyring.set_password(identifier, cls.username, value)
        except KeyringError as e:
            raise AssertionException("Error in setting credentials '{0}' : {1}".format(identifier, str(e)))
        except Exception as e:
            if "stub received bad data" in str(e):
                raise AssertionException("Value for {0} too long for backend to store: {1}".format(identifier, str(e)))
            raise e

    def store(self):
        for k, v in self.config_files.items():
            self.logger.info("Analyzing: " + k)
            v.store()

    def retrieve(self):
        pass

    def revert(self):
        pass

    def load_configs(self):
        """
        This method will be responsible for reading all config files specified in user-sync-config.yml
        so that credential manager knows which keys and values are needed per file
        """
        root_cfg = ConfigFileLoader.load_root_config(self.root_config)

        # fragile
        umapis = ConfigLoader.as_list(root_cfg['adobe_users']['connectors']['umapi'])
        connectors = root_cfg['directory_users']['connectors']

        for u in umapis:
            self.config_files[u] = UmapiCredentialConfig(u)

        for c, v in connectors.items():
            if c == "ldap":
                self.config_files[v] = LdapCredentialConfig(v)
            elif c == "okta":
                self.config_files[v] = OktaCredentialConfig(v)
            elif c == "console":
                self.config_files[v] = ConsoleCredentialConfig(v)

        print()


class CredentialConfig:
    """
    Each method (store, revert, fetch) should be written in a subclass of this class.  This will help keep
    it all organized since filenames and config is stored within.  Shared methods are get_key, load and save.
    """

    def __init__(self, filename=None):
        # filename will be the unique identifier for each file.  This can be an absolute path - but if so we cannot
        # move the sync tool.  More to consider here....
        self.filename = filename

        # The dictionary including comments that will be updated and re-saved
        self.load()

    def store(self):
        # Store will explicitly save all targeted keys
        # For example:
        # CredentialManager.set(filename + ":password", "1234)
        # Then update self.config to match with secure key
        # save file
        pass

    def revert(self):
        # calls fetch first to get values
        # Then updates config to replace secure key format with value
        # save file
        pass

    def retrieve(self):
        # probably should return a dictionary for the config using CredentialManager.get()
        # Maybe looks like:
        # {
        #   'connector-ldap.yml:password': '1234'
        # }
        # where self.get_key(password) will return the full identifier
        # don't update config since this is meant to get the values only - revert will persist
        pass

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
            raise AssertionException("Cannot store key - value not found for: {0}".format(key_list))
        if not self.parse_secure_key(value):
            k = self.get_qualified_identifier(key_list)
            CredentialManager.set(k, value)
            self.set_nested_key(key_list, {'secure': k})

    def retrieve_key(self, key_list):
        """
        Retrieves the value (if any) for key_list, and updates the config if revert=True
        Returns a dictionary of identifiers and values for this config
        :param key_list:
        :return:
        """
        key_list = ConfigLoader.as_list(key_list)
        secure_identifier = self.parse_secure_key(self.get_nested_key(key_list))
        if secure_identifier is not None:
            return CredentialManager.get(secure_identifier)

    def revert_key(self, key_list):
        plaintext_cred = self.retrieve_key(key_list)
        if plaintext_cred is None:
            raise AssertionException('No secure key found for given identifier.')
        self.set_nested_key(key_list, plaintext_cred)
        return plaintext_cred

    def parse_secure_key(self, value):
        """
        Returns the identifier for the secure key if present, or else None
        The queried key must be a string if not secured, or a properly formatted dictionary
        containing exactly one key named 'secure' whose value is the identifier in keyring.
        """
        if value is None:
            raise AssertionException("Key is missing or emtpy:" + str(value))
        if isinstance(value, dict):
            if len(value) == 1 and 'secure' in value:
                return value['secure']
            raise AssertionException("Invalid secure key format for '{0}'. Dict should have "
                                     "exactly one key called 'secure': {1}".format(value, value))
        elif not isinstance(value, six.text_type):
            raise AssertionException("Invalid credential format for '{0}'.  "
                                     "Key must be dict or string: {1}".format(value, value))


class LdapCredentialConfig(CredentialConfig):
    """
    Example config provided
    """

    def store(self):
        self.store_key(['password'])
        self.save()

    def revert(self):
        creds = {}
        creds['password'] = self.revert_key(['password'])
        self.save()
        return creds

    def retrieve(self):
        creds = {}
        creds['password'] = self.retrieve_key(['password'])
        return creds


class UmapiCredentialConfig(CredentialConfig):
    """
    Example config provided
    """

    def store(self):
        self.store_key(['enterprise', 'org_id'])
        self.store_key(['enterprise', 'api_key'])
        self.store_key(['enterprise', 'client_secret'])
        self.store_key(['enterprise', 'tech_acct'])
        self.save()

    def revert(self):
        creds = {}
        creds['enterprise'] = {
            'org_id': self.revert_key(['enterprise', 'org_id']),
            'api_key': self.revert_key(['enterprise', 'api_key']),
            'client_secret': self.revert_key(['enterprise', 'client_secret']),
            'tech_acct': self.revert_key(['enterprise', 'tech_acct'])
        }
        self.save()
        return creds

    def retrieve(self):
        creds = {}
        creds['enterprise'] = {
            'org_id': self.retrieve_key(['enterprise', 'org_id']),
            'api_key': self.retrieve_key(['enterprise', 'api_key']),
            'client_secret': self.retrieve_key(['enterprise', 'client_secret']),
            'tech_acct': self.retrieve_key(['enterprise', 'tech_acct'])
        }
        return creds


class OktaCredentialConfig(CredentialConfig):
    """
    Example config provided
    """

    def store(self):
        self.store_key(['api_token'])
        self.save()

    def revert(self):
        creds = {}
        creds['api_token'] = self.revert_key(['api_token'])
        self.save()
        return creds

    def retrieve(self):
        creds = {}
        creds['api_token'] = self.retrieve_key(['api_token'])
        return creds


class ConsoleCredentialConfig(CredentialConfig):
    """
    Example config provided
    """

    def store(self):
        self.store_key(['integration', 'org_id'])
        self.store_key(['integration', 'api_key'])
        self.store_key(['integration', 'client_secret'])
        self.store_key(['integration', 'tech_acct'])
        self.save()

    def revert(self):
        creds = {}
        creds['integration'] = {
            'org_id': self.revert_key(['integration', 'org_id']),
            'api_key': self.revert_key(['integration', 'api_key']),
            'client_secret': self.revert_key(['integration', 'client_secret']),
            'tech_acct': self.revert_key(['integration', 'tech_acct'])
        }
        self.save()
        return creds

    def retrieve(self):
        creds = {}
        creds['integration'] = {
            'org_id': self.retrieve_key(['integration', 'org_id']),
            'api_key': self.retrieve_key(['integration', 'api_key']),
            'client_secret': self.retrieve_key(['integration', 'client_secret']),
            'tech_acct': self.retrieve_key(['integration', 'tech_acct'])
        }
        return creds
