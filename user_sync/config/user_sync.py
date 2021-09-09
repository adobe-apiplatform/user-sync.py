# Copyright (c) 2016-2017 Adobe Inc.  All rights reserved.
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
from copy import deepcopy

import six
import yaml

import user_sync.helper
import user_sync.identity_type
from user_sync import flags
from user_sync.engine import umapi as rules
from user_sync.engine.common import AdobeGroup, PRIMARY_TARGET_NAME
from user_sync.error import AssertionException
from .common import DictConfig, ConfigLoader, ConfigFileLoader, resolve_invocation_options, as_list, resolve_invocation_options, validate_max_limit_config


class UMAPIConfigLoader(ConfigLoader):
    """
    Loads config files and does pathname expansion on settings that refer to files or directories
    """
    # key_paths in the root configuration file that should have filename values
    # mapped to their value options.  See load_from_yaml for the option meanings.
    ROOT_CONFIG_PATH_KEYS = {'/adobe_users/connectors/umapi': (True, True, None),
                             '/directory_users/connectors/*': (True, False, None),
                             '/directory_users/extension': (True, False, None),
                             '/logging/file_log_directory': (False, False, "logs"),
                             }

    # like ROOT_CONFIG_PATH_KEYS, but for non-root configuration files
    SUB_CONFIG_PATH_KEYS = {'/enterprise/priv_key_path': (True, False, None),
                            '/integration/priv_key_path': (True, False, None)}

    # default values for reading configuration files
    # these are in alphabetical order!  Always add new ones that way!
    config_defaults = {
        'config_encoding': 'utf8',
        'config_filename': 'user-sync-config.yml',
    }

    # default values for options that can be specified on the command line
    # these are in alphabetical order!  Always add new ones that way!
    invocation_defaults = {
        'adobe_only_user_action': ['preserve'],
        'adobe_only_user_list': None,
        'adobe_users': ['all'],
        'config_filename': 'user-sync-config.yml',
        'connector': ['ldap'],
        'encoding_name': 'utf8',
        'exclude_unmapped_users': False,
        'process_groups': False,
        'ssl_cert_verify': True,
        'strategy': 'sync',
        'test_mode': False,
        'update_user_info': False,
        'user_filter': None,
        'users': ['all']
    }

    def __init__(self, args):
        """
        Load the config files and invocation options.

        :type args: dict
        """
        self.logger = logging.getLogger('config')
        self.args = args
        self.main_config = self.load_main_config()
        self.invocation_options = self.load_invocation_options()
        self.directory_groups = self.load_directory_groups()

    def load_main_config(self):
        """Load the main configuration file and return its content as a config object.
        :rtype: DictConfig
        """
        config_filename = self.args['config_filename'] or self.config_defaults['config_filename']
        config_encoding = self.args['encoding_name'] or self.config_defaults['config_encoding']
        try:
            codecs.lookup(config_encoding)
        except LookupError:
            raise AssertionException("Unknown encoding '%s' specified for configuration files" % config_encoding)
        self.logger.info("Using main config file: %s (encoding %s)", config_filename, config_encoding)
        self.config_loader = ConfigFileLoader(config_encoding, self.ROOT_CONFIG_PATH_KEYS, self.SUB_CONFIG_PATH_KEYS)
        main_config_content = self.config_loader.load_root_config(config_filename)
        return DictConfig("<%s>" % config_filename, main_config_content)

    def get_invocation_options(self):
        return self.invocation_options

    def load_invocation_options(self):
        """Merge the invocation option defaults with overrides from the main config and the command line.
        :rtype: dict
        """

        # copy instead of direct assignment to preserve original invocation_defaults object
        # otherwise, setting options also sets invocation_defaults (same memory ref)
        options = deepcopy(self.invocation_defaults)

        invocation_config = self.main_config.get_dict_config('invocation_defaults', True)
        options = resolve_invocation_options(options, invocation_config, self.invocation_defaults, self.args)

        # now process command line options.  the order of these is important,
        # because options processed later depend on the values of those processed earlier

        # --connector
        connector_spec = options['connector']
        connector_type = user_sync.helper.normalize_string(connector_spec[0])
        if connector_type in ["ldap", "okta", "adobe_console"]:
            if len(connector_spec) > 1:
                raise AssertionException('Must not specify a file (%s) with connector type %s' %
                                         (connector_spec[0], connector_type))
            options['directory_connector_type'] = connector_type
        elif connector_type == "csv":
            if len(connector_spec) != 2:
                raise AssertionException("You must specify a single file with connector type csv")
            options['directory_connector_type'] = 'csv'
            options['directory_connector_overridden_options'] = {'file_path': connector_spec[1]}
        else:
            raise AssertionException('Unknown connector type: %s' % connector_type)

        # --adobe-only-user-action
        if options['strategy'] == 'push':
            options['adobe_only_user_action'] = None
            self.logger.info("Strategy push: ignoring default adobe-only-user-action")
        else:
            adobe_action_spec = options['adobe_only_user_action']
            adobe_action = user_sync.helper.normalize_string(adobe_action_spec[0])
            options['stray_list_output_path'] = None
            if adobe_action == 'preserve':
                pass  # no option settings needed
            elif adobe_action == 'exclude':
                options['exclude_strays'] = True
            elif adobe_action == 'write-file':
                if len(adobe_action_spec) != 2:
                    raise AssertionException('You must specify a single file for adobe-only-user-action "write-file"')
                options['stray_list_output_path'] = adobe_action_spec[1]
            elif adobe_action == 'delete':
                options['delete_strays'] = True
            elif adobe_action == 'remove':
                options['remove_strays'] = True
            elif adobe_action == 'remove-adobe-groups':
                options['disentitle_strays'] = True
            else:
                raise AssertionException('Unknown option "%s" for adobe-only-user-action' % adobe_action)

        # --users and --adobe-only-user-list conflict with each other, so we need to disambiguate.

        stray_list_input_path = None
        if options['adobe_only_user_list']:
            # specifying --adobe-only-user-list overrides the configuration file default for --users
            if options['strategy'] == 'push':
                raise AssertionException('You cannot specify --adobe-only-user-list when using "push" strategy')
            options['users'] = None
            self.logger.info("Adobe-only user list specified, ignoring 'users' setting")
            stray_list_input_path = options['adobe_only_user_list']

        users_spec = None

        if options['users'] is not None:
            users_spec = options['users']

        # --users
        if users_spec:
            users_action = user_sync.helper.normalize_string(users_spec[0])
            if users_action == 'all':
                if options['directory_connector_type'] == 'okta':
                    raise AssertionException('Okta connector module does not support "--users all"')
            elif users_action == 'file':
                if options['directory_connector_type'] == 'csv':
                    raise AssertionException('You cannot specify file input with both "users" and "connector" options')
                if len(users_spec) != 2:
                    raise AssertionException('You must specify the file to read when using the users "file" option')
                options['directory_connector_type'] = 'csv'
                options['directory_connector_overridden_options'] = {'file_path': users_spec[1]}
            elif users_action == 'mapped':
                options['directory_group_mapped'] = True
            elif users_action == 'group':
                if len(users_spec) != 2:
                    raise AssertionException('You must specify the groups to read when using the users "group" option')
                options['directory_group_filter'] = users_spec[1].split(',')
            else:
                raise AssertionException('Unknown option "%s" for users' % users_action)

        # --adobe-only-user-list
        if stray_list_input_path:
            if options['stray_list_output_path'] is not None:
                raise AssertionException('You cannot specify both an adobe-only-user-list (%s) and '
                                         'an adobe-only-user-action of "write-file"')
            # don't read the directory when processing from the stray list
            self.logger.info('adobe-only-user-list specified, so not reading or comparing directory and Adobe users')
            options['stray_list_input_path'] = stray_list_input_path

        # --user-filter
        if stray_list_input_path:
            options['user_filter'] = None
            self.logger.info("adobe-only-user-list specified, so ignoring default user filter specification")

        if options['user_filter'] is not None:
            username_filter_pattern = options['user_filter']
            try:
                compiled_expression = re.compile(r'\A' + username_filter_pattern + r'\Z', re.IGNORECASE)
            except Exception as e:
                raise AssertionException("Bad regular expression in user filter: %s reason: %s" %
                                         (username_filter_pattern, e))
            options['username_filter_regex'] = compiled_expression

        # --adobe-users
        adobe_users_spec = None
        if options['adobe_users'] is not None:
            adobe_users_spec = options['adobe_users']

        if adobe_users_spec is not None:
            adobe_users_action = user_sync.helper.normalize_string(adobe_users_spec[0])
            if adobe_users_action == 'all':
                options['adobe_group_mapped'] = False
            elif adobe_users_action == 'mapped':
                options['adobe_group_mapped'] = True
            elif adobe_users_action == 'group':
                if len(adobe_users_spec) != 2:
                    raise AssertionException(
                        'You must specify the groups to read when using the adobe-users "group" option')
                options['adobe_group_filter'] = []
                for group in adobe_users_spec[1].split(','):
                    options['adobe_group_filter'].append(AdobeGroup.create(group))
            else:
                raise AssertionException('Unknown option "%s" for adobe-users' % adobe_users_action)

        return options

    def get_logging_config(self):
        return self.main_config.get_dict_config('logging', True)

    def get_target_options(self):
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
            if isinstance(item, str):
                if secondary_config_sources:
                    # if we see a string after a dict, the user has done something wrong, and we fail.
                    raise AssertionException("Secondary umapi configuration found with no prefix: " + item)
                primary_config_sources.append(item)
            elif isinstance(item, dict):
                for key, val in six.iteritems(item):
                    secondary_config_sources[key] = as_list(val)
        primary_config = self.create_umapi_options(primary_config_sources)
        secondary_configs = {key: self.create_umapi_options(val)
                             for key, val in six.iteritems(secondary_config_sources)}
        return primary_config, secondary_configs

    def get_directory_connector_module_name(self):
        """
        :rtype str
        """
        if self.invocation_options.get('stray_list_input_path', None):
            return None
        connector_type = self.invocation_options.get('directory_connector_type')
        if connector_type:
            return 'user_sync.connector.directory_' + connector_type
        else:
            return None

    def get_directory_connector_configs(self):
        connectors_config = None
        directory_config = self.main_config.get_dict_config('directory_users', True)
        if directory_config is not None:
            connectors_config = directory_config.get_dict_config('connectors', True)
        # make sure none of the standard connectors get reported as unused
        if connectors_config:
            connectors_config.get_list('ldap', True)
            connectors_config.get_list('csv', True)
            connectors_config.get_list('okta', True)
            connectors_config.get_list('adobe_console', True)
        return connectors_config

    def get_directory_connector_options(self, connector_name):
        """
        :rtype dict
        """
        options = {}
        connectors_config = self.get_directory_connector_configs()
        if connectors_config is None:
            raise AssertionException("Missing key 'connectors' in directory_users")
        if connector_name != 'csv' and connector_name not in connectors_config.value:
            raise AssertionException("Config file must be specified for connector type :: '{}'".format(connector_name))

        if connectors_config is not None:
            connector_item = connectors_config.get_list(connector_name, True)
            options = self.get_dict_from_sources(connector_item)
            if connector_name == "adobe_console":
                options['ssl_cert_verify'] = self.invocation_options['ssl_cert_verify']
        options = self.combine_dicts(
            [options, self.invocation_options.get('directory_connector_overridden_options', {})])

        return options

    def get_directory_groups(self):
        return self.directory_groups

    def load_directory_groups(self):
        """
        :rtype dict(str, list(AdobeGroup))
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
                group = AdobeGroup.create(adobe_group)
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
        elif isinstance(value, list):
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
            config = self.config_loader.load_sub_config(source)
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

    def get_engine_options(self):
        """
        Return a dict representing options for RuleProcessor.
        """
        options = deepcopy(rules.RuleProcessor.default_options)
        options.update(self.invocation_options)

        # process directory configuration options
        directory_config = self.main_config.get_dict_config('directory_users', True)
        if not directory_config:
            raise AssertionException("'directory_users' must be specified")

        # account type
        new_account_type = directory_config.get_string('user_identity_type', True)
        new_account_type = user_sync.identity_type.parse_identity_type(new_account_type)
        if new_account_type:
            options['new_account_type'] = new_account_type
        else:
            self.logger.debug("Using default for new_account_type: %s", options['new_account_type'])
        # country code
        default_country_code = directory_config.get_string('default_country_code', True)
        if default_country_code:
            options['default_country_code'] = default_country_code
        additional_groups = directory_config.get_list('additional_groups', True) or []
        try:
            additional_groups = [{'source': re.compile(r['source']),
                                  'target': AdobeGroup.create(r['target'], index=False)}
                                 for r in additional_groups]
        except Exception as e:
            raise AssertionException("Additional group rule error: {}".format(str(e)))
        options['additional_groups'] = additional_groups
        sync_options = directory_config.get_dict_config('group_sync_options', True)
        if sync_options:
            options['auto_create'] = sync_options.get_bool('auto_create', True)

        # process exclusion configuration options
        adobe_config = self.main_config.get_dict_config('adobe_users', True)
        if not adobe_config:
            raise AssertionException("'adobe_users' must be specified")

        exclude_identity_type_names = adobe_config.get_list('exclude_identity_types', True)
        if exclude_identity_type_names:
            exclude_identity_types = []
            for name in exclude_identity_type_names:
                message_format = 'Illegal value in exclude_identity_types: %s'
                identity_type = user_sync.identity_type.parse_identity_type(name, message_format)
                exclude_identity_types.append(identity_type)
            options['exclude_identity_types'] = exclude_identity_types
        exclude_users_regexps = adobe_config.get_list('exclude_users', True)
        if exclude_users_regexps:
            exclude_users = []
            for regexp in exclude_users_regexps:
                try:
                    # add "match begin" and "match end" markers to ensure complete match
                    # and compile the patterns because we will use them over and over
                    exclude_users.append(re.compile(r'\A' + regexp + r'\Z', re.UNICODE | re.IGNORECASE))
                except re.error as e:
                    validation_message = ('Illegal regular expression (%s) in %s: %s' %
                                          (regexp, 'exclude_identity_types', e))
                    raise AssertionException(validation_message)
            options['exclude_users'] = exclude_users
        exclude_group_names = adobe_config.get_list('exclude_adobe_groups', True) or []
        if exclude_group_names:
            exclude_groups = []
            for name in exclude_group_names:
                group = AdobeGroup.create(name)
                if not group or group.get_umapi_name() != PRIMARY_TARGET_NAME:
                    validation_message = 'Illegal value for %s in config file: %s' % ('exclude_groups', name)
                    if not group:
                        validation_message += ' (Not a legal group name)'
                    else:
                        validation_message += ' (Can only exclude groups in primary organization)'
                    raise AssertionException(validation_message)
                exclude_groups.append(group.get_group_name())
            options['exclude_groups'] = exclude_groups

        # get the limits
        limits_config = self.main_config.get_dict_config('limits')
        max_missing = limits_config.get_value('max_adobe_only_users', (int, str), False)
        options['max_adobe_only_users'] = validate_max_limit_config(max_missing)
        
        # now get the directory extension, if any
        extension_config = self.get_directory_extension_options()
        options['extension_enabled'] = flags.get_flag('UST_EXTENSION')
        if extension_config and not options['extension_enabled']:
            self.logger.warning('Extension config functionality is disabled - skipping after-map hook')
        elif extension_config:
            after_mapping_hook_text = extension_config.get_string('after_mapping_hook')
            options['after_mapping_hook'] = compile(after_mapping_hook_text, '<per-user after-mapping-hook>', 'exec')
            options['extended_attributes'].update(extension_config.get_list('extended_attributes', True))
            # declaration of extended adobe groups: this is needed for two reasons:
            # 1. it allows validation of group names, and matching them to adobe groups
            # 2. it allows removal of adobe groups not assigned by the hook
            for extended_adobe_group in extension_config.get_list('extended_adobe_groups', True) or []:
                group = AdobeGroup.create(extended_adobe_group)
                if group is None:
                    message = 'Extension contains illegal extended_adobe_group spec: ' + str(extended_adobe_group)
                    raise AssertionException(message)

        # set the directory group filter from the mapping, if requested.
        # This must come late, after any prior adds to the mapping from other parameters.
        if options.get('directory_group_mapped'):
            options['directory_group_filter'] = set(six.iterkeys(self.directory_groups))

        # set the adobe group filter from the mapping, if requested.
        if options.get('adobe_group_mapped') is True:
            options['adobe_group_filter'] = set(AdobeGroup.iter_groups())

        return options

    def create_umapi_options(self, connector_config_sources):
        options = self.get_dict_from_sources(connector_config_sources)
        options['test_mode'] = self.invocation_options['test_mode']
        options['ssl_cert_verify'] = self.invocation_options['ssl_cert_verify']
        return options

    def check_unused_config_keys(self):
        directory_connectors_config = self.get_directory_connector_configs()
        self.main_config.report_unused_values(self.logger, [directory_connectors_config])
