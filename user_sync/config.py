# Copyright (c) 2016-2017 Adobe Systems Incorporated.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import codecs
import logging
import os
import re
import subprocess
import types

import yaml
import six

import user_sync.identity_type
import user_sync.rules
import user_sync.port

from user_sync.error import AssertionException

DEFAULT_MAIN_CONFIG_FILENAME = 'user-sync-config.yml'


class ConfigLoader(object):
    def __init__(self, caller_options):
        """
        :type caller_options: dict
        """
        self.options = options = {
            # these are in alphabetical order!  Always add new ones that way!
            'delete_strays': False,
            'config_file_encoding': 'utf8',
            'directory_connector_module_name': None,
            'directory_connector_overridden_options': None,
            'directory_group_filter': None,
            'directory_group_mapped': False,
            'disentitle_strays': False,
            'exclude_strays': False,
            'main_config_filename': DEFAULT_MAIN_CONFIG_FILENAME,
            'manage_groups': False,
            'remove_strays': False,
            'strategy': 'sync',
            'stray_list_input_path': None,
            'stray_list_output_path': None,
            'test_mode': False,
            'update_user_info': True,
            'username_filter_regex': None,
        }
        options.update(caller_options)
        main_config_filename = options.get('main_config_filename')
        config_encoding = options['config_file_encoding']
        try:
            codecs.lookup(config_encoding)
        except LookupError:
            raise AssertionException("Unknown encoding '%s' specified with --config-file-encoding" % config_encoding)
        ConfigFileLoader.config_encoding = config_encoding
        main_config_content = ConfigFileLoader.load_root_config(main_config_filename)
        self.logger = logger = logging.getLogger('config')
        logger.info("Using main config file: %s", main_config_filename)
        self.main_config = DictConfig("<%s>" % main_config_filename, main_config_content)

    def set_options(self, caller_options):
        """
        :type caller_options: dict
        """
        self.options.update(caller_options)

    def get_logging_config(self):
        return self.main_config.get_dict_config('logging', True)

    def get_umapi_options(self):
        """
        Read and return the primary and secondary umapi connector configs.
        The primary is a singleton, the secondaries are a map from name to config.
        The syntax in the config file is rather complex, which makes this code a bit complex;
        be sure you read the detailed docs before trying to read this function.
        We also check for and err out gracefully if it's a v1-style config file.
        :return: tuple: (primary, secondary_map)
        """
        if self.main_config.get_dict_config('dashboard', True):
            raise AssertionException("Your main configuration file is still in v1 format.  Please convert it to v2.")
        adobe_users_config = self.main_config.get_dict_config('adobe_users', True)
        if not adobe_users_config:
            return {}, {}
        connector_config = adobe_users_config.get_dict_config('connectors', True)
        if not connector_config:
            return {}, {}
        umapi_config = connector_config.get_list('umapi', True)
        if not umapi_config:
            return {}, {}
        # umapi_config is a list of strings (primary umapi source files) followed by a
        # list of dicts (secondary umapi source specifications, whose keys are umapi names
        # and whose values are a list of config file strings)
        secondary_config_sources = {}
        primary_config_sources = []
        for item in umapi_config:
            if isinstance(item, six.string_types):
                if secondary_config_sources:
                    # if we see a string after a dict, the user has done something wrong, and we fail.
                    raise AssertionException("Secondary umapi configuration found with no prefix: " + item)
                primary_config_sources.append(item)
            elif isinstance(item, dict):
                for key, val in six.iteritems(item):
                    secondary_config_sources[key] = self.as_list(val)
        primary_config = self.create_umapi_options(primary_config_sources)
        secondary_configs = {key: self.create_umapi_options(val)
                             for key, val in six.iteritems(secondary_config_sources)}
        return primary_config, secondary_configs

    def get_directory_connector_module_name(self):
        """
        :rtype str
        """
        connector_type = self.options.get('directory_connector_type')
        if connector_type:
            return 'user_sync.connector.directory_' + connector_type
        else:
            return None

    def get_directory_connector_configs(self):
        connectors_config = None
        directory_config = self.main_config.get_dict_config('directory_users', True)
        if directory_config is not None:
            connectors_config = directory_config.get_dict_config('connectors', True)
        # make sure neither ldap nor csv connectors get reported as unused
        if connectors_config:
            connectors_config.get_list('ldap', True)
            connectors_config.get_list('csv', True)
        return connectors_config

    def get_directory_connector_options(self, connector_name):
        """
        :rtype dict
        """
        options = {}
        connectors_config = self.get_directory_connector_configs()
        if connectors_config is not None:
            connector_item = connectors_config.get_list(connector_name, True)
            options = self.get_dict_from_sources(connector_item)
        options = self.combine_dicts([options, self.options['directory_connector_overridden_options']])
        return options

    def get_directory_groups(self):
        """
        :rtype dict(str, list(user_sync.rules.AdobeGroup))
        """
        adobe_groups_by_directory_group = {}
        if self.main_config.get_dict_config('directory', True):
            raise AssertionException("Your main configuration file is still in v1 format.  Please convert it to v2.")
        groups_config = None
        directory_config = self.main_config.get_dict_config('directory_users', True)
        if directory_config is not None:
            groups_config = directory_config.get_list_config('groups', True)
        if groups_config is None:
            return adobe_groups_by_directory_group

        for item in groups_config.iter_dict_configs():
            directory_group = item.get_string('directory_group')
            groups = adobe_groups_by_directory_group.get(directory_group)
            if groups is None:
                adobe_groups_by_directory_group[directory_group] = groups = []

            adobe_groups = item.get_list('adobe_groups', True)
            for adobe_group in adobe_groups or []:
                group = user_sync.rules.AdobeGroup.create(adobe_group)
                if group is None:
                    validation_message = ('Bad adobe group: "%s" in directory group: "%s"' %
                                          (adobe_group, directory_group))
                    raise AssertionException(validation_message)
                groups.append(group)

        return adobe_groups_by_directory_group

    def get_directory_extension_options(self):
        """
        Read the directory extension, if there is one, and return its dictionary of options
        :return: dict
        """
        options = {}
        directory_config = self.main_config.get_dict_config('directory_users', True)
        if directory_config:
            sources = directory_config.get_list('extension', True)
            if sources:
                options = DictConfig('extension', self.get_dict_from_sources(sources))
                if options:
                    after_mapping_hook_text = options.get_string('after_mapping_hook', True)
                    if after_mapping_hook_text is None:
                        raise AssertionError("No after_mapping_hook found in extension configuration")
        return options

    @staticmethod
    def as_list(value):
        if value is None:
            return []
        elif isinstance(value, user_sync.port.list_type):
            return value
        return [value]

    def get_dict_from_sources(self, sources):
        """
        Given a list of config file paths, return the dictionary composed of all the contents
        of those config files, or None if the list is empty
        :param sources: a list of strings
        :rtype dict
        """
        if not sources:
            return {}
        options = []
        for source in sources:
            config = ConfigFileLoader.load_sub_config(source)
            options.append(config)
        return self.combine_dicts(options)

    @staticmethod
    def parse_string(format_string, string_value):
        """
        :type format_string: str
        :type string_value: str
        :rtype dict
        """
        regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', format_string)
        values = list(re.search(regex, string_value).groups())
        keys = re.findall(r'{(.+?)}', format_string)
        _dict = dict(zip(keys, values))
        return _dict

    @staticmethod
    def combine_dicts(dicts):
        """
        Return a single dict from an iterable of dicts.  Each dict is merged into the resulting dict, 
        with a latter dict possibly overwriting the keys from previous dicts.
        :type dicts: list(dict)
        :rtype dict
        """
        result = {}
        for dict_item in dicts:
            if isinstance(dict_item, dict):
                for dict_key, dict_val in six.iteritems(dict_item):
                    result_val = result.get(dict_key)
                    if isinstance(result_val, dict) and isinstance(dict_val, dict):
                        result_val.update(dict_val)
                    else:
                        result[dict_key] = dict_val
        return result

    def get_rule_options(self):
        """
        Return a dict representing options for RuleProcessor.
        """
        # process directory configuration options
        new_account_type = None
        default_country_code = None
        directory_config = self.main_config.get_dict_config('directory_users', True)
        if directory_config:
            new_account_type = directory_config.get_string('user_identity_type', True)
            new_account_type = user_sync.identity_type.parse_identity_type(new_account_type)
            default_country_code = directory_config.get_string('default_country_code', True)
        if not new_account_type:
            new_account_type = user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE
            self.logger.debug("Using default for new_account_type: %s", new_account_type)

        # process exclusion configuration options
        exclude_identity_types = exclude_identity_type_names = []
        exclude_users = exclude_users_regexps = []
        exclude_groups = exclude_group_names = []
        adobe_config = self.main_config.get_dict_config('adobe_users', True)
        if adobe_config:
            exclude_identity_type_names = adobe_config.get_list('exclude_identity_types', True) or []
            exclude_users_regexps = adobe_config.get_list('exclude_users', True) or []
            exclude_group_names = adobe_config.get_list('exclude_adobe_groups', True) or []
        for name in exclude_identity_type_names:
            message_format = 'Illegal value in exclude_identity_types: %s'
            identity_type = user_sync.identity_type.parse_identity_type(name, message_format)
            exclude_identity_types.append(identity_type)
        for regexp in exclude_users_regexps:
            try:
                # add "match begin" and "match end" markers to ensure complete match
                # and compile the patterns because we will use them over and over
                exclude_users.append(re.compile(r'\A' + regexp + r'\Z', re.UNICODE))
            except re.error as e:
                validation_message = ('Illegal regular expression (%s) in %s: %s' %
                                      (regexp, 'exclude_identity_types', e))
                raise AssertionException(validation_message)
        for name in exclude_group_names:
            group = user_sync.rules.AdobeGroup.create(name)
            if not group or group.get_umapi_name() != user_sync.rules.PRIMARY_UMAPI_NAME:
                validation_message = 'Illegal value for %s in config file: %s' % ('exclude_groups', name)
                if not group:
                    validation_message += ' (Not a legal group name)'
                else:
                    validation_message += ' (Can only exclude groups in primary organization)'
                raise AssertionException(validation_message)
            exclude_groups.append(group.get_group_name())

        # get the limits
        limits_config = self.main_config.get_dict_config('limits')
        max_adobe_only_users = limits_config.get_int('max_adobe_only_users')

        # now get the directory extension, if any
        after_mapping_hook = None
        extended_attributes = None
        extension_config = self.get_directory_extension_options()
        if extension_config:
            after_mapping_hook_text = extension_config.get_string('after_mapping_hook')
            after_mapping_hook = compile(after_mapping_hook_text, '<per-user after-mapping-hook>', 'exec')
            extended_attributes = extension_config.get_list('extended_attributes')
            # declaration of extended adobe groups: this is needed for two reasons:
            # 1. it allows validation of group names, and matching them to adobe groups
            # 2. it allows removal of adobe groups not assigned by the hook
            for extended_adobe_group in extension_config.get_list('extended_adobe_groups'):
                group = user_sync.rules.AdobeGroup.create(extended_adobe_group)
                if group is None:
                    message = 'Extension contains illegal extended_adobe_group spec: ' + str(extended_adobe_group)
                    raise AssertionException(message)

        options = self.options
        result = {
            # these are in alphabetical order!  Always add new ones that way!
            'after_mapping_hook': after_mapping_hook,
            'default_country_code': default_country_code,
            'delete_strays': options['delete_strays'],
            'directory_group_filter': options['directory_group_filter'],
            'directory_group_mapped': options['directory_group_mapped'],
            'disentitle_strays': options['disentitle_strays'],
            'exclude_groups': exclude_groups,
            'exclude_identity_types': exclude_identity_types,
            'exclude_strays': options['exclude_strays'],
            'exclude_users': exclude_users,
            'extended_attributes': extended_attributes,
            'manage_groups': options['manage_groups'],
            'max_adobe_only_users': max_adobe_only_users,
            'new_account_type': new_account_type,
            'strategy': options['strategy'],
            'remove_strays': options['remove_strays'],
            'stray_list_input_path': options['stray_list_input_path'],
            'stray_list_output_path': options['stray_list_output_path'],
            'test_mode': options['test_mode'],
            'update_user_info': options['update_user_info'],
            'username_filter_regex': options['username_filter_regex'],
        }
        return result

    def create_umapi_options(self, connector_config_sources):
        options = self.get_dict_from_sources(connector_config_sources)
        options['test_mode'] = self.options['test_mode']
        return options

    def check_unused_config_keys(self):
        directory_connectors_config = self.get_directory_connector_configs()
        self.main_config.report_unused_values(self.logger, [directory_connectors_config])


class ObjectConfig(object):
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
        for child_config in six.itervalues(self.child_configs):
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
        if types_to_describe == six.string_types:
            result = self.describe_types(user_sync.port.string_type)
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
        return six.iterkeys(self.value)

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
        value = self.get_value(key, dict, none_allowed)
        return value

    def get_string(self, key, none_allowed=False):
        return self.get_value(key, six.string_types, none_allowed)

    def get_int(self, key, none_allowed=False):
        return self.get_value(key, user_sync.port.integer_type, none_allowed)

    def get_bool(self, key, none_allowed=False):
        return self.get_value(key, user_sync.port.boolean_type, none_allowed)

    def get_list(self, key, none_allowed=False):
        value = self.get_value(key, None, none_allowed)
        if value is not None and not isinstance(value, list):
            value = [value]
        return value

    def get_list_config(self, key, none_allowed=False):
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
                import keyring
                value = keyring.get_password(service_name=secure_value_key, username=user_name)
            except Exception as e:
                raise AssertionException('%s: Error accessing secure storage: %s' % (scope, e))
        else:
            value = cleartext_value
        if not value and not none_allowed:
            raise AssertionException(
                '%s: No value in secure storage for user "%s", key "%s"' % (scope, user_name, secure_value_key))
        return value


class ConfigFileLoader:
    """
    Loads config files and does pathname expansion on settings that refer to files or directories
    """
    # config files can contain Unicode characters, so an encoding for them
    # can be specified as a command line argument.  This defaults to utf8.
    config_encoding = 'utf8'

    # key_paths in the root configuration file that should have filename values
    # mapped to their value options.  See load_from_yaml for the option meanings.
    ROOT_CONFIG_PATH_KEYS = {'/adobe_users/connectors/umapi': (True, True, None),
                             '/directory_users/connectors/*': (True, False, None),
                             '/directory_users/extension': (True, False, None),
                             '/logging/file_log_directory': (False, False, "logs"),
                             }

    # like ROOT_CONFIG_PATH_KEYS, but for non-root configuration files
    SUB_CONFIG_PATH_KEYS = {'/enterprise/priv_key_path': (True, False, None)}

    @classmethod
    def load_root_config(cls, filename):
        """
        loads the specified file as a root configuration file. This basically
        means that on top of loading the file as a yaml file into a dictionary,
        it will apply the ROOT_CONFIG_PATH_KEYS to the dictionary to replace
        the specified paths with absolute path values that are resolved
        relative to the given configuration's filename.
        type filename: str
        rtype dict
        """
        return cls.load_from_yaml(filename, cls.ROOT_CONFIG_PATH_KEYS)

    @classmethod
    def load_sub_config(cls, filename):
        """
        same as load_root_config, but applies SUB_CONFIG_PATH_KEYS to the
        dictionary loaded from the yaml file.
        """
        return cls.load_from_yaml(filename, cls.SUB_CONFIG_PATH_KEYS)

    @classmethod
    def load_other_config(cls, filename):
        """
        same as load_root_config, but does no post-processing.
        :type filename: str
        """
        return cls.load_from_yaml(filename, {})

    # these are set by load_from_yaml to hold the current state of what
    # key_path is being searched for in what file in what directory
    filepath = None  # absolute path of file currently being loaded
    filename = None  # filename of file currently being loaded
    dirpath = None   # directory path of file currently being loaded
    key_path = None  # the full pathname of the setting key being processed

    @classmethod
    def load_from_yaml(cls, filename, path_keys):
        """
        loads a yaml file, processes the resulting dict to adapt values for keys
        (the path to which is defined in path_keys) to a value that represents
        a file reference relative to the source file being loaded, and returns the
        processed dict.
        :param filename: the file to load yaml from
        :param path_keys: a dict whose keys are "path_keys" such as /key1/key2/key3
                          and whose values are tuples: (must_exist, can_have_subdict, default_val)
                          which are options on the value of the key whose values
                          are path expanded: must the path exist, can it be a list of paths
                          that contains sub-dictionaries whose values are paths, and
                          does the key have a default value so that must be added to
                          the dictionary if there is not already a value found.
        """
        if filename.startswith('$(') and filename.endswith(')'):
            # it's a command line to execute and read standard output
            dir_end = filename.index(']')
            if filename.startswith('$([') and dir_end > 0:
                dir_name = filename[3:dir_end]
                cmd_name = filename[dir_end + 1:-1]
            else:
                dir_name = os.path.abspath(".")
                cmd_name = filename[3:-1]
            try:
                byte_string = subprocess.check_output(cmd_name, cwd=dir_name, shell=True)
                yml = yaml.load(byte_string.decode(cls.config_encoding, 'strict'))
            except subprocess.CalledProcessError as e:
                raise AssertionException("Error executing process '%s' in dir '%s': %s" % (cmd_name, dir_name, e))
            except UnicodeDecodeError as e:
                raise AssertionException('Encoding error in process output: %s' % e)
            except yaml.error.MarkedYAMLError as e:
                raise AssertionException('Error parsing process YAML data: %s' % e)
        else:
            # it's a pathname to a configuration file to read
            cls.filepath = os.path.abspath(filename)
            if not os.path.isfile(cls.filepath):
                raise AssertionException('No such configuration file: %s' % (cls.filepath,))
            cls.filename = os.path.split(cls.filepath)[1]
            cls.dirpath = os.path.dirname(cls.filepath)
            try:
                with open(filename, 'rb', 1) as input_file:
                    byte_string = input_file.read()
                    yml = yaml.load(byte_string.decode(cls.config_encoding, 'strict'))
            except IOError as e:
                # if a file operation error occurred while loading the
                # configuration file, swallow up the exception and re-raise it
                # as an configuration loader exception.
                raise AssertionException("Error reading configuration file '%s': %s" % (cls.filepath, e))
            except UnicodeDecodeError as e:
                # as above, but in case of encoding errors
                raise AssertionException("Encoding error in configuration file '%s: %s" % (cls.filepath, e))
            except yaml.error.MarkedYAMLError as e:
                # as above, but in case of parse errors
                raise AssertionException("Error parsing configuration file '%s': %s" % (cls.filepath, e))

        # process the content of the dict
        if yml is None:
            # empty YML files are parsed as None
            yml = {}
        elif not isinstance(yml, dict):
            # malformed YML files produce a non-dictionary
            raise AssertionException("Configuration file '%s' does not contain settings" % cls.filepath)
        for path_key, options in six.iteritems(path_keys):
            cls.key_path = path_key
            keys = path_key.split('/')
            cls.process_path_key(yml, keys, 1, *options)
        return yml

    @classmethod
    def process_path_key(cls, dictionary, keys, level, must_exist, can_have_subdict, default_val):
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
                for key, val in six.iteritems(dictionary):
                    dictionary[key] = cls.process_path_value(val, must_exist, can_have_subdict)
            elif key in dictionary:
                dictionary[key] = cls.process_path_value(dictionary[key], must_exist, can_have_subdict)
            # key was not found, but default value was set, so apply it
            elif default_val:
                dictionary[key] = cls.relative_path(default_val, must_exist)
        # otherwise recurse deeper into the dict
        elif level < len(keys) - 1:
            key = keys[level]
            # if a wildcard is specified at this level, this indicates this
            # should select all keys that have dict type values, and recurse
            # into them at the next level
            if key == "*":
                for key in dictionary.keys():
                    if isinstance(dictionary[key], dict):
                        cls.process_path_key(dictionary[key], keys, level + 1,
                                             must_exist, can_have_subdict, default_val)
            elif key in dictionary:
                # if the key refers to a dictionary, recurse into it to go
                # further down the path key
                if isinstance(dictionary[key], dict):
                    cls.process_path_key(dictionary[key], keys, level + 1, must_exist, can_have_subdict, default_val)
            # if the key was not found, but a default value is specified,
            # drill down further to set the default value
            elif default_val:
                dictionary[key] = {}
                cls.process_path_key(dictionary[key], keys, level + 1, must_exist, can_have_subdict, default_val)

    @classmethod
    def process_path_value(cls, val, must_exist, can_have_subdict):
        """
        does the relative path processing for a value from the dictionary,
        which can be a string, a list of strings, or a list of strings
        and "tagged" strings (sub-dictionaries whose values are strings)
        :param val: the value we are processing, for error messages
        :param must_exist: whether there must be a value
        :param can_have_subdict: whether the value can be a tagged string
        """
        if isinstance(val, six.string_types):
            return cls.relative_path(val, must_exist)
        elif isinstance(val, list):
            vals = []
            for entry in val:
                if can_have_subdict and isinstance(entry, dict):
                    for subkey, subval in six.iteritems(entry):
                        vals.append({subkey: cls.relative_path(subval, must_exist)})
                else:
                    vals.append(cls.relative_path(entry, must_exist))
            return vals

    @classmethod
    def relative_path(cls, val, must_exist):
        """
        returns an absolute path that is resolved relative to the file being loaded
        """
        if not isinstance(val, six.string_types):
            raise AssertionException("Expected pathname for setting %s in config file %s" %
                                     (cls.key_path, cls.filename))
        if val.startswith('$(') and val.endswith(')'):
            # this presumes
            return "$([" + cls.dirpath + "]" + val[2:-1] + ")"
        if cls.dirpath and not os.path.isabs(val):
            val = os.path.abspath(os.path.join(cls.dirpath, val))
        if must_exist and not os.path.isfile(val):
            raise AssertionException('In setting %s in config file %s: No such file %s' %
                                     (cls.key_path, cls.filename, val))
        return val


class OptionsBuilder(object):
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
        self.set_value(key, user_sync.port.boolean_type, default_value)

    def set_int_value(self, key, default_value):
        """
        :type key: str
        :type default_value: int
        """
        self.set_value(key, user_sync.port.integer_type, default_value)

    def set_string_value(self, key, default_value):
        """
        :type key: str
        :type default_value: Optional(str)
        """
        self.set_value(key, six.string_types, default_value)

    def set_dict_value(self, key, default_value):
        """
        :type key: str
        :type default_value: dict
        """
        self.set_value(key, dict, default_value)

    def set_value(self, key, allowed_types, default_value):
        value = default_value
        config = self.default_config
        if config is not None and key in config:
            value = config.get_value(key, allowed_types, False)
        self.options[key] = value

    def require_string_value(self, key):
        return self.require_value(key, six.string_types)

    def require_value(self, key, allowed_types):
        config = self.default_config
        if config is None:
            raise AssertionException("No config found.")
        self.options[key] = value = config.get_value(key, allowed_types)
        return value
