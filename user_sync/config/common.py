import logging
import os

import re
# import six
import yaml
from abc import ABC, abstractmethod

import user_sync.helper
import user_sync.identity_type
from user_sync.error import AssertionException


class ConfigLoader(ABC):
    @abstractmethod
    def get_invocation_options(self):
        pass

    @abstractmethod
    def get_directory_groups(self):
        pass

    @abstractmethod
    def get_engine_options(self) -> dict:
        pass

    @abstractmethod
    def get_directory_connector_module_name(self) -> str:
        pass

    @abstractmethod
    def get_directory_connector_options(self, name: str) -> dict:
        pass

    @abstractmethod
    def get_target_options(self) -> tuple[dict, dict]:
        pass

    @abstractmethod
    def check_unused_config_keys(self):
        pass

    @abstractmethod
    def get_logging_config(self):
        pass


class ObjectConfig:
    def __init__(self, scope):
        """
        :type scope: str
        """
        self.parent = None
        self.child_configs = {}
        self.scope = scope

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, config):
        """
        :type config: ObjectConfig
        """
        config.set_parent(self)
        self.child_configs[config.scope] = config

    def find_child_config(self, scope):
        return self.child_configs.get(scope)

    def iter_configs(self):
        """
        :rtype iterable(ObjectConfig)
        """
        yield self
        for child_config in self.child_configs.values():
            for subtree_config in child_config.iter_configs():
                yield subtree_config

    def get_full_scope(self):
        scopes = []
        config = self
        while config is not None:
            scopes.insert(0, str(config.scope))
            config = config.parent
        return '.'.join(scopes)

    def create_assertion_error(self, message):
        return AssertionException("%s in: %s" % (message, self.get_full_scope()))

    def describe_types(self, types_to_describe):
        if types_to_describe == str:
            result = self.describe_types(str)
        elif isinstance(types_to_describe, tuple):
            result = []
            for type_to_describe in types_to_describe:
                result.extend(self.describe_types(type_to_describe))
        else:
            result = [types_to_describe.__name__]
        return result

    def report_unused_values(self, logger, optional_configs=None):
        optional_configs = [] if optional_configs is None else optional_configs
        has_error = False
        for config in self.iter_configs():
            messages = config.describe_unused_values()
            if len(messages) > 0:
                if config in optional_configs:
                    log_level = logging.WARNING
                else:
                    log_level = logging.ERROR
                    has_error = True
                for message in messages:
                    logger.log(log_level, message)

        if has_error:
            raise AssertionException('Detected unused keys that are not ignorable.')

    def describe_unused_values(self):
        return []


class ListConfig(ObjectConfig):
    def __init__(self, scope, value):
        """
        :type scope: str
        :type value: list
        """
        super(ListConfig, self).__init__(scope)
        self.value = value

    def iter_values(self, allowed_types):
        """
        :type allowed_types
        """
        index = 0
        for item in self.value:
            if not isinstance(item, allowed_types):
                reported_types = self.describe_types(allowed_types)
                raise self.create_assertion_error("Value should be one of these types: %s for index: %s" %
                                                  (reported_types, index))
            index += 1
            yield item

    def iter_dict_configs(self):
        index = 0
        for value in self.iter_values(dict):
            config = self.find_child_config(index)
            if config is None:
                config = DictConfig("[%s]" % index, value)
                self.add_child(config)
            yield config
            index += 1


class DictConfig(ObjectConfig):
    def __init__(self, scope, value):
        """
        :type scope: str
        :type value: dict
        """
        super(DictConfig, self).__init__(scope)
        self.value = value
        self.accessed_keys = set()

    def __contains__(self, item):
        return item in self.value

    def iter_keys(self):
        return self.value.keys()

    def iter_unused_keys(self):
        for key in self.iter_keys():
            if key not in self.accessed_keys:
                yield key

    def get_dict_config(self, key, none_allowed=False):
        """
        :rtype DictConfig
        """
        result = self.find_child_config(key)
        if result is None:
            value = self.get_dict(key, none_allowed)
            if value is not None:
                result = DictConfig(key, value)
                self.add_child(result)
        return result

    def get_dict(self, key, none_allowed=False):
        """
        :rtype: dict
        """
        value = self.get_value(key, dict, none_allowed)
        return value

    def get_string(self, key, none_allowed=False) -> str:
        """
        :rtype: basestring
        """
        return self.get_value(key, str, none_allowed)

    def get_int(self, key, none_allowed=False):
        """
        :rtype: int
        """
        return self.get_value(key, int, none_allowed)

    def get_bool(self, key, none_allowed=False):
        """
        :rtype: bool
        """
        return self.get_value(key, bool, none_allowed)

    def get_list(self, key, none_allowed=False):
        """
        :rtype: list
        """
        value = self.get_value(key, None, none_allowed)
        if value is not None and not isinstance(value, list):
            value = [value]
        return value

    def get_list_config(self, key, none_allowed=False) -> ListConfig:
        """
        :rtype ListConfig
        """
        result = self.find_child_config(key)
        if result is None:
            value = self.get_list(key, none_allowed)
            if value is not None:
                result = ListConfig(key, value)
                self.add_child(result)
        return result

    def get_value(self, key, allowed_types, none_allowed=False):
        self.accessed_keys.add(key)
        result = self.value.get(key)
        if result is None:
            if not none_allowed:
                raise self.create_assertion_error("Value not found for key: %s" % key)
        elif allowed_types is not None and not isinstance(result, allowed_types):
            reported_types = self.describe_types(allowed_types)
            raise self.create_assertion_error("Value should be one of these types: %s for key: %s" %
                                              (reported_types, key))
        return result

    def describe_unused_values(self):
        messages = []
        unused_keys = list(self.iter_unused_keys())
        if len(unused_keys) > 0:
            messages.append("Found unused keys: %s in: %s" % (unused_keys, self.get_full_scope()))
        return messages

    keyring_prefix = 'secure_'
    keyring_suffix = '_key'

    def has_credential(self, name):
        """
        Check if there is a credential setting with the given name
        :param name: plaintext setting name for the credential
        :return: setting that was specified, or None if none was
        """
        scope = self.get_full_scope()
        keyring_name = self.keyring_prefix + name + self.keyring_suffix
        plaintext = self.get_string(name, True)
        secure = self.get_string(keyring_name, True)
        if plaintext and secure:
            raise AssertionException('%s: cannot contain setting for both "%s" and "%s"' % (scope, name, keyring_name))
        if plaintext is not None:
            return name
        elif secure is not None:
            return keyring_name
        else:
            return None

    def get_credential(self, name, user_name, none_allowed=False):
        """
        Get the credential with the given name.  Raises an AssertionException if there
        is no credential, or if the credential is specified both in plaintext and the keyring.
        If the credential is kept in the keyring, the value of the keyring_name setting
        gives the secure storage key, and we fetch that key for the given user.
        :param name: setting name for the plaintext credential
        :param user_name: the user for whom we should fetch the service name password in secure storage
        :param none_allowed: whether the credential can be missing or empty
        :return: credential string
        """
        keyring_name = self.keyring_prefix + name + self.keyring_suffix
        scope = self.get_full_scope()
        # sometimes the credential is in plain text
        cleartext_value = self.get_string(name, True)
        # sometimes the value is in the keyring
        secure_value_key = self.get_string(keyring_name, True)
        # but it has to be in exactly one of those two places!
        if not cleartext_value and not secure_value_key and not none_allowed:
            raise AssertionException('%s: must contain setting for "%s" or "%s"' % (scope, name, keyring_name))
        if cleartext_value and secure_value_key:
            raise AssertionException('%s: cannot contain setting for both "%s" and "%s"' % (scope, name, keyring_name))
        if secure_value_key:
            try:
                value = self.get_value_from_keyring(secure_value_key, user_name)
            except Exception as e:
                raise AssertionException('%s: Error accessing secure storage: %s' % (scope, e))
        else:
            value = cleartext_value
        if not value and not none_allowed:
            raise AssertionException(
                '%s: No value in secure storage for user "%s", key "%s"' % (scope, user_name, secure_value_key))
        return value

    @staticmethod
    def get_value_from_keyring(secure_value_key, user_name):
        import keyrings.cryptfile.cryptfile
        keyrings.cryptfile.cryptfile.CryptFileKeyring.keyring_key = "none"

        import keyring
        if (isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring) or
                isinstance(keyring.get_keyring(), keyring.backends.chainer.ChainerBackend)):
            keyring.set_keyring(keyrings.cryptfile.cryptfile.CryptFileKeyring())

        logging.getLogger("keyring").info(
            "Using keyring '" + keyring.get_keyring().name + "' to retrieve: " + secure_value_key)
        return keyring.get_password(service_name=secure_value_key, username=user_name)


class ConfigFileLoader:

    def __init__(self, encoding: str, root_path_keys: dict, sub_path_keys: dict):
        self.encoding = encoding
        self.root_path_keys = root_path_keys
        self.sub_path_keys = sub_path_keys

    def load_root_config(self, filename: str) -> dict:
        """
        loads the specified file as a root configuration file. This basically
        means that on top of loading the file as a yaml file into a dictionary,
        it will apply the ROOT_CONFIG_PATH_KEYS to the dictionary to replace
        the specified paths with absolute path values that are resolved
        relative to the given configuration's filename.
        type filename: str
        rtype dict
        """
        return self.load_from_yaml(filename, self.root_path_keys)

    def load_sub_config(self, filename: str) -> dict:
        """
        same as load_root_config, but applies SUB_CONFIG_PATH_KEYS to the
        dictionary loaded from the yaml file.
        """
        return self.load_from_yaml(filename, self.sub_path_keys)

    def load_other_config(self, filename: str) -> dict:
        """
        same as load_root_config, but does no post-processing.
        :type filename: str
        """
        return self.load_from_yaml(filename, {})

    def load_from_yaml(self, filepath, path_keys):
        """
        loads a yaml file, processes the resulting dict to adapt values for keys
        (the path to which is defined in path_keys) to a value that represents
        a file reference relative to the source file being loaded, and returns the
        processed dict.
        :param filepath: the file to load yaml from
        :param path_keys: a dict whose keys are "path_keys" such as /key1/key2/key3
                          and whose values are tuples: (must_exist, can_have_subdict, default_val)
                          which are options on the value of the key whose values
                          are path expanded: must the path exist, can it be a list of paths
                          that contains sub-dictionaries whose values are paths, and
                          does the key have a default value so that must be added to
                          the dictionary if there is not already a value found.
        """
        if filepath.startswith('$(') and filepath.endswith(')'):
            raise AssertionException("Shell execution is no longer supported: {}".format(filepath))

        filepath = os.path.abspath(filepath)
        if not os.path.isfile(filepath):
            raise AssertionException('No such configuration file: {}'.format(filepath))
        filename = os.path.split(filepath)[1]
        dirpath = os.path.dirname(filepath)
        try:
            with open(filepath, 'rb', 0) as input_file:
                byte_string = input_file.read()
                yml = yaml.safe_load(byte_string.decode(self.encoding, 'strict'))
        except IOError as e:
            # if a file operation error occurred while loading the
            # configuration file, swallow up the exception and re-raise it
            # as an configuration loader exception.
            raise AssertionException("Error reading configuration file '{}': {}".format(filepath, e))
        except UnicodeDecodeError as e:
            # as above, but in case of encoding errors
            raise AssertionException("Encoding error in configuration file '{}: {}".format(filepath, e))
        except yaml.error.MarkedYAMLError as e:
            # as above, but in case of parse errors
            raise AssertionException("Error parsing configuration file '{}': {}".format(filepath, e))

        # process the content of the dict
        if yml is None:
            # empty YML files are parsed as None
            return {}
        if not isinstance(yml, dict):
            # malformed YML files produce a non-dictionary
            raise AssertionException("Configuration file or command '{}' does not contain settings".format(filepath))
        for path_key, options in path_keys.items():
            key_path = path_key
            keys = path_key.split('/')
            self.process_path_key(dirpath, filename, key_path, yml, keys, 1, *options)
        return yml

    def process_path_key(self, dirpath, filename, key_path, dictionary, keys, level, must_exist, can_have_subdict, default_val):
        """
        this function is given the list of keys in the current key_path, and searches
        recursively into the given dictionary until it finds the designated value, and then
        resolves relative values in that value to abspaths based on the current filename.
        If a default value for the key_path is given, and no value is found in the dictionary,
        then the key_path is added to the dictionary with the expanded default value.
        type dictionary: dict
        type keys: list
        type level: int
        type must_exist: boolean
        type can_have_subdict: boolean
        type default_val: any
        """
        # found the key_path, process values
        if level == len(keys) - 1:
            key = keys[level]
            # if a wildcard is specified at this level, that means we
            # should process all keys as path values
            if key == "*":
                for key, val in dictionary.items():
                    dictionary[key] = self.process_path_value(dirpath, filename, key_path, val, must_exist, can_have_subdict)
            elif key in dictionary:
                dictionary[key] = self.process_path_value(dirpath, filename, key_path, dictionary[key], must_exist, can_have_subdict)
            # key was not found, but default value was set, so apply it
            elif default_val:
                dictionary[key] = self.relative_path(dirpath, filename, key_path, default_val, must_exist)
        # otherwise recurse deeper into the dict
        elif level < len(keys) - 1:
            key = keys[level]
            if key in dictionary:
                # if the key refers to a dictionary, recurse into it to go
                # further down the path key
                if isinstance(dictionary[key], dict):
                    self.process_path_key(dirpath, filename, key_path, dictionary[key], keys, level + 1,
                                          must_exist, can_have_subdict, default_val)
            # if the key was not found, but a default value is specified,
            # drill down further to set the default value
            elif default_val:
                dictionary[key] = {}
                self.process_path_key(dirpath, filename, key_path, dictionary[key], keys, level + 1,
                                      must_exist, can_have_subdict, default_val)

    def process_path_value(self, dirpath, filename, key_path, val, must_exist, can_have_subdict):
        """
        does the relative path processing for a value from the dictionary,
        which can be a string, a list of strings, or a list of strings
        and "tagged" strings (sub-dictionaries whose values are strings)
        :param val: the value we are processing, for error messages
        :param must_exist: whether there must be a value
        :param can_have_subdict: whether the value can be a tagged string
        """
        if isinstance(val, str):
            return self.relative_path(dirpath, filename, key_path, val, must_exist)
        elif isinstance(val, list):
            vals = []
            for entry in val:
                if can_have_subdict and isinstance(entry, dict):
                    for subkey, subval in entry.items():
                        vals.append({subkey: self.relative_path(dirpath, filename, key_path, subval, must_exist)})
                else:
                    vals.append(self.relative_path(dirpath, filename, key_path, entry, must_exist))
            return vals

    @staticmethod
    def relative_path(dirpath, filename, key_path, val, must_exist):
        """
        returns an absolute path that is resolved relative to the file being loaded
        """
        if not isinstance(val, str):
            raise AssertionException("Expected pathname for setting {} in config file {}".format(key_path, filename))
        if val.startswith('$(') and val.endswith(')'):
            raise AssertionException("Shell execution is no longer supported: {}".format(val))
        if dirpath and not os.path.isabs(val):
            val = os.path.abspath(os.path.join(dirpath, val))
        if must_exist and not os.path.isfile(val):
            raise AssertionException('In setting {} in config file {}: No such file {}'.format(key_path, filename, val))
        return val


class OptionsBuilder:
    def __init__(self, default_config):
        """
        :type default_config: DictConfig
        """
        self.default_config = default_config
        self.options = {}

    def get_options(self):
        return self.options

    def set_bool_value(self, key, default_value):
        """
        :type key: str
        :type default_value: bool
        """
        self.set_value(key, bool, default_value)

    def set_int_value(self, key, default_value):
        """
        :type key: str
        :type default_value: int
        """
        self.set_value(key, int, default_value)

    def set_string_value(self, key, default_value):
        """
        :type key: str
        :type default_value: Optional(str)
        """
        self.set_value(key, str, default_value)

    def set_dict_value(self, key, default_value):
        """
        :type key: str
        :type default_value: dict or None
        """
        self.set_value(key, dict, default_value)

    def set_value(self, key, allowed_types, default_value):
        value = default_value
        config = self.default_config
        if config is not None and key in config:
            value = config.get_value(key, allowed_types, False)
        self.options[key] = value

    def require_string_value(self, key):
        return self.require_value(key, str)

    def require_value(self, key, allowed_types):
        config = self.default_config
        if config is None:
            raise AssertionException("No config found.")
        self.options[key] = value = config.get_value(key, allowed_types)
        return value
        
        
def resolve_invocation_options(options: dict, invocation_config: DictConfig, invocation_defaults: dict, args: dict) -> dict:
    # get overrides from the main config
    if invocation_config:
        for k, v in invocation_defaults.items():
            if isinstance(v, bool):
                val = invocation_config.get_bool(k, True)
                if val is not None:
                    options[k] = val
            elif isinstance(v, list):
                val = invocation_config.get_list(k, True)
                if val:
                    options[k] = val
            else:
                val = invocation_config.get_string(k, True)
                if val:
                    options[k] = val

    # now handle overrides from CLI options
    for k, arg_val in args.items():
        if arg_val is None:
            continue
        options[k] = arg_val
    return options


def as_list(value):
    if value is None:
        return []
    elif isinstance(value, list):
        return value
    return [value]

def as_set(value):
    return set(as_list(value))

def validate_max_limit_config(max_missing):
    percent_pattern = re.compile(r"(\d*(\.\d+)?%)")
    if isinstance(max_missing, str) and percent_pattern.match(max_missing):
        max_missing_percent = float(max_missing.strip('%'))
        if 0.0 <= max_missing_percent <= 100.0:
            options_param = max_missing
        else:
            raise AssertionException("max_adobe_only_users value must be less or equal than 100%")
    else:
        try:
            options_param = int(max_missing)
        except ValueError:
            raise AssertionException("Unable to parse max_adobe_only_users value. Value must be a percentage or an integer.")
    return options_param

def check_max_limit(stray_count, max_missing_option, primary_user_count, secondary_user_count, console, logger, org_string=""):
    if isinstance(max_missing_option, str) and '%' in max_missing_option:
        percent = float(max_missing_option.strip('%')) / 100
        max_missing = int(primary_user_count - secondary_user_count) * percent
    else:
        max_missing = max_missing_option
    if stray_count > max_missing:
        logger.critical('%sUnable to process %s-only users, as their count (%s) is larger '
                                'than the max_adobe_only_users setting (%s)', org_string, console, stray_count, max_missing_option)
        return False
    else:
        return True
