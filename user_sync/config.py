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

import glob
import logging
import os
import re
import types
import yaml

from user_sync import credential_manager
import user_sync.error
import user_sync.identity_type
import user_sync.rules

DEFAULT_MAIN_CONFIG_FILENAME = 'user-sync-config.yml'
DEFAULT_DASHBOARD_OWNING_CONFIG_FILENAME = 'dashboard-owning-config.yml'
DEFAULT_DASHBOARD_ACCESSOR_CONFIG_FILENAME_FORMAT = 'dashboard-accessor-{organization_name}-config.yml'

class ConfigLoader(object):
    def __init__(self, caller_options):
        '''
        loads the configuration, given the configuration file info
        :type caller_options: dict
        '''
        # default configuration options
        self.options = options = {
            # these are in alphabetical order!  Always add new ones that way!
            'delete_list_output_path': None,
            'delete_nonexistent_users': False,
            'delete_user_key_list': None,
            'directory_connector_module_name': None,
            'directory_connector_overridden_options': None,
            'directory_group_filter': None,
            'directory_group_mapped': False,
            'directory_source_filters': None,
            'main_config_filename': DEFAULT_MAIN_CONFIG_FILENAME,
            'manage_groups': False,
            'remove_list_output_path': None,
            'remove_nonexistent_users': False,
            'remove_user_key_list': None,
            'test_mode': False,
            'update_user_info': True,
            'username_filter_regex': None,
        }
        
        # merge custom options with our default options
        self.update_options(caller_options)   

        # get the main config filename
        main_config_filename = options.get('main_config_filename')
        
        # halt if the config file does not exist
        if (not os.path.isfile(main_config_filename)):
            raise user_sync.error.AssertionException('Config file does not exist: %s' % (main_config_filename))  
        
        self.directory_source_filters_accessed = set()        
        
        # load the actual configuration file content and build the
        # configuration object
        self.logger = logger = logging.getLogger('config')
        logger.info("Using main config file: %s", main_config_filename)
        
        self.main_config_content = ConfigFileLoader(main_config_filename)
        self.main_config = DictConfig("<%s>" % main_config_filename, self.main_config_content.content)
        
    def update_options(self, caller_options):          
        '''
        update configuration with the new options
        :type caller_options: dict
        '''
        self.options.update(caller_options)        
        
    def get_logging_config(self):
        '''
        return the logging settings from the configuration file
        :rtype dict
        '''
        return self.main_config.get_dict_config('logging', True)

    def get_dashboard_options_for_owning(self):
        '''
        load and return dashboard configuration for the owning organization
        :rtype dict
        '''
        # load the default dashboard configuration file
        owning_config_filename = None

        # get the owning dashboard configuration path, if the user entered one
        dashboard_config = self.main_config.get_dict_config('dashboard', True)
        if dashboard_config:
            owning_config_filenames = dashboard_config.get_list('owning', True)
            # should only have one owning configuration
            if owning_config_filenames:
                owning_config_filename = self.main_config_content.get_relative_filename(owning_config_filenames[0])
        
        # get the default owning dashboard configuration filename, if no
        # custom one was provided
        if not owning_config_filename:
            owning_config_filename = self.main_config_content.get_relative_filename(DEFAULT_DASHBOARD_OWNING_CONFIG_FILENAME)

        additional_owning_config_sources = []
        
        # add custom test configuration
        additional_owning_config_sources.append({
            'test_mode': self.options['test_mode']
        })
        
        # build dashboard options given sources
        return self.create_dashboard_options(owning_config_filename, additional_owning_config_sources, 'owning_dashboard') 
    
    def get_dashboard_options_for_accessors(self):
        '''
        load and return dashboard configuration for accessors
        :rtype dict
        '''
        # get the dashboard configuration settings
        dashboard_config = self.main_config.get_dict_config('dashboard', True)

        # load the accessor config filename format
        accessor_config_filename_format = None
        if dashboard_config:
            accessor_config_filename_format = dashboard_config.get_string('accessor_config_filename_format', True)
        # if no configuration file format is loaded, use the default
        if not accessor_config_filename_format:
            accessor_config_filename_format = DEFAULT_DASHBOARD_ACCESSOR_CONFIG_FILENAME_FORMAT
        
        # apply configuration file filter, and build map of organization names
        # to configuration files
        accessor_config_file_paths = {}
        accessor_config_filename_wildcard = accessor_config_filename_format.format(**{'organization_name': '*'})
        for file_path in glob.glob1(self.main_config_content.dirpath, accessor_config_filename_wildcard):
            parse_result = self.parse_string(accessor_config_filename_format, file_path)
            organization_name = parse_result.get('organization_name')
            if organization_name:
                accessor_config_file_paths[organization_name] = self.main_config_content.get_relative_filename(file_path)

        # get the configuration for the accessors
        accessors_config = None
        if dashboard_config:
            accessors_config = dashboard_config.get_dict_config('accessors', True)

        # build a list of organization names
        accessors_options = {}
        organization_names = set(accessor_config_file_paths.iterkeys())
        if accessors_config:
            organization_names.update(accessors_config.iter_keys())
        
        # build dashboard configuration for the organizations
        for organization_name in organization_names:
            # first, load the accessor configuration file returned from the
            # filename pattern matcher
            accessor_config_filename = accessor_config_file_paths.get(organization_name, None)

            # accessor configuration files specified directly in dashboard
            # accessors takes precedence over the file mapped in the file
            # pattern
            if accessors_config:
                accessor_config_filename = self.main_config_content.get_relative_filename(accessors_config.get_list(organization_name, True))

            additional_accessor_config_sources = []
            
            # add test mode sources
            additional_accessor_config_sources.append({
                'test_mode': self.options['test_mode']
            })
            
            # build dashboard options given sources
            accessors_options[organization_name] = self.create_dashboard_options(accessor_config_filename, additional_accessor_config_sources, 'accessor_dashboard[%s]' % organization_name)
            
        return accessors_options
    
    def get_directory_connector_module_name(self):
        '''
        :rtype str
        '''
        options = self.options
        return options['directory_connector_module_name']
    
    def get_directory_connector_configs(self):
        connectors_config = None
        directory_config = self.main_config.get_dict_config('directory', True)
        if directory_config != None:
            connectors_config = directory_config.get_dict_config('connectors', True)
        return connectors_config
    
    def get_directory_connector_options(self, connector_name):
        '''
        :rtype dict
        '''                
        connector_options = {}
        
        # get the directory connector configuration if available
        connectors_config = self.get_directory_connector_configs()
        if connectors_config:
            connector_item = connectors_config.get_list(connector_name, True)
            connector_options = self.get_dict_from_sources(connector_item, 'directory[%s]' % connector_name)
        
        # determine which source filter configuration files we should use
        source_filter_sources = self.as_list(connector_options.get('source_filter'))
        directory_source_filters = self.options['directory_source_filters']
        if directory_source_filters:
            self.directory_source_filters_accessed.add(connector_name)

            # get the dictionary for the source filter file. Assume file is
            # relative to the working directory
            directory_source_list = self.as_list(directory_source_filters.get(connector_name))
            source_filter_dict = self.get_dict_from_sources(directory_source_list,'directory[%s].source_filters' % connector_name)
            
            # ensure it contains an 'all_users_filter'
            if not source_filter_dict.get('all_users_filter'):
                self.logger.warn('Ignoring source filter for directory[%s] as "all_users_filter" was not specified' % connector_name)
            else:
                source_filter_sources.append(directory_source_filters.get(connector_name))
                
        # load source filters
        source_filters =  self.get_dict_from_sources(source_filter_sources, 'directory[%s].source_filters' % connector_name)
        if source_filters:
            connector_options['source_filters'] = source_filters
        
        configs = [connector_options, self.options['directory_connector_overridden_options']]
        current_config = combine_dicts(configs)
        credential_config_source = credential_manager.get_credentials(credential_manager.DIRECTORY_CREDENTIAL_TYPE, connector_name, config = current_config, config_loader = self)
        return self.get_dict_from_sources([current_config, credential_config_source], "directory_credential_manager")
    
    def get_directory_groups(self):
        '''
        load the customer group to Adobe dashboard groups mappings model from
        the loaded configuration
        :rtype dict(str, list(user_sync.rules.DashboardGroup))
        '''
        adobe_groups_by_directory_group = {}
        groups_config = None

        # get the directory:group: configuration settings        
        directory_config = self.main_config.get_dict_config('directory', True)
        if directory_config:
            groups_config = directory_config.get_list_config('groups', True)         
        
        # if there is no group configuration return empty mapping
        if not groups_config:
            return adobe_groups_by_directory_group
        
        # process customer groups
        for item in groups_config.iter_dict_configs():
            directory_group = item.get_string('directory_group')
            
            # get ready to process Adobe dashboard groups
            groups = adobe_groups_by_directory_group.get(directory_group)
            if not groups:
                adobe_groups_by_directory_group[directory_group] = groups = []

            # process dashboard groups mapped to customer group
            dashboard_groups_config = item.get_list_config('dashboard_groups')
            for dashboard_group in dashboard_groups_config.iter_values(types.StringTypes):
                # create the configuration model group based on the mapping
                # settings
                group = user_sync.rules.DashboardGroup.create(dashboard_group)
                if not group:
                    validation_message = 'Bad dashboard group: "%s" in directory group: "%s"' % (dashboard_group, directory_group)
                    raise user_sync.error.AssertionException(validation_message)
                groups.append(group)

        return adobe_groups_by_directory_group

    @staticmethod    
    def as_list(value):
        if (value == None):
            return []
        elif isinstance(value, types.ListType):
            return value
        return [value]
        
    def get_dict_from_sources(self, sources, owner):
        '''
        combine various configuration sources into a single combined dictionary
        :type sources: list
        :rtype dict
        '''
        # sources are empty or None, return an empty dictionary
        if not sources:
            return {}
        
        # process sources
        options = []
        for source in sources: 
            # if the specified source is a string, treat it as a path to a
            # file containing the source containing a dict
            if (isinstance(source, types.StringTypes)):
                absolute_path = self.get_absolute_file_path(source)
                if (os.path.isfile(absolute_path)):
                    config = load_from_yaml(absolute_path)
                    options.append(config)
                else:
                    raise user_sync.error.AssertionException('Cannot find file: %s for: %s' % (absolute_path, owner))
                
            # if the source is a dict, add it to  our collection of dicts
            elif isinstance(source, dict):
                options.append(source)
                
            # if the source was invalid, raise this
            elif source:
                raise user_sync.error.AssertionException('Source should be a filename or a dictionary for: %s' % owner)
            
        # combine all source dicts to a single one
        return combine_dicts(options)
    
    def get_absolute_file_path(self, value):
        '''
        If value is an absolute path, return as is.  Otherwise, if value is a relative path, 
        make sure the path is relative from the config path.
        :type value: str
        '''        
        path = value if os.path.isabs(value) else self.get_file_path(value)
        return path
    
    def get_file_path(self, filename):
        '''
        :type filename: str
        :rtype str
        '''        
        directory = self.main_config_content.dirpath
        path = os.path.join(directory, filename)
        return path

    @staticmethod
    def parse_string(format_string, string_value):
        '''
        :type format_string: str
        :type string_value: str
        :rtype dict
        '''
        regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', format_string)
        values = list(re.search(regex, string_value).groups())
        keys = re.findall(r'{(.+?)}', format_string)
        _dict = dict(zip(keys, values))
        return _dict

    def get_rule_options(self):
        '''
        Return a dict representing options for RuleProcessor.
        rtype: dict
        '''
        # process directory configuration options
        new_account_type = None
        default_country_code = None
        directory_config = self.main_config.get_dict_config('directory', True)
        if directory_config:
            new_account_type = directory_config.get_string('user_identity_type', True)
            new_account_type = user_sync.identity_type.parse_identity_type(new_account_type)
            default_country_code = directory_config.get_string('default_country_code', True)
        if not new_account_type:
            new_account_type = user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE
            self.logger.info("Using default for new_account_type: %s", new_account_type)

        # process exclusion configuration options
        exclude_identity_types = exclude_identity_type_names = []
        exclude_users = exclude_users_regexps = []
        exclude_groups = exclude_group_names = []
        dashboard_config = self.main_config.get_dict_config('dashboard', True)
        if dashboard_config:
            exclude_identity_type_names = dashboard_config.get_list('exclude_identity_types', True) or []
            exclude_users_regexps = dashboard_config.get_list('exclude_users', True) or []
            exclude_group_names = dashboard_config.get_list('exclude_groups', True) or []
        for name in exclude_identity_type_names:
            identity_type = user_sync.identity_type.parse_identity_type(name)
            if not identity_type:
                validation_message = 'Illegal value for %s in config file: %s' % ('exclude_identity_types', name)
                raise user_sync.error.AssertionException(validation_message)
            exclude_identity_types.append(identity_type)
        for regexp in exclude_users_regexps:
            try:
                # add "match begin" and "match end" markers to ensure complete match
                # and compile the patterns because we will use them over and over
                exclude_users.append(re.compile(r'\A' + regexp + r'\Z', re.UNICODE))
            except re.error as e:
                validation_message = ('Illegal regular expression (%s) in %s: %s' %
                                      (regexp, 'exclude_identity_types', e))
                raise user_sync.error.AssertionException(validation_message)
        for name in exclude_group_names:
            group = user_sync.rules.DashboardGroup.create(name)
            if not group or group.get_organization_name() != user_sync.rules.OWNING_ORGANIZATION_NAME:
                validation_message = 'Illegal value for %s in config file: %s' % ('exclude_groups', name)
                if not group:
                    validation_message += ' (Not a legal group name)'
                else:
                    validation_message += ' (Can only exclude groups in owning organization)'
                raise user_sync.error.AssertionException(validation_message)
            exclude_groups.append(group.get_group_name())

        # setup rule processor limits
        limits_config = self.main_config.get_dict_config('limits')
        max_deletions_per_run = limits_config.get_int('max_deletions_per_run')
        max_missing_users = limits_config.get_int('max_missing_users')

        after_mapping_hook = None
        extended_attributes = None
        extensions_config = self.main_config.get_list_config('extensions', True)
        
        # setup extensions configurations
        if extensions_config:
            for extension_config in extensions_config.iter_dict_configs():
                context = extension_config.get_string('context')

                # context must be per-user
                if context != 'per-user':
                    self.logger.warning("Unrecognized extension context '%s' ignored", context)
                    continue
                
                # shouldn't have more than one extension
                if after_mapping_hook:
                    self.logger.warning("Duplicate extension context '%s' ignored", context)
                    continue

                # load the after mapping hook source
                after_mapping_hook_text = extension_config.get_string('after_mapping_hook')
                if not after_mapping_hook_text:
                    self.logger.warning("No valid hook found in extension with context '%s'; extension ignored")
                    continue

                # compile hook
                after_mapping_hook = compile(after_mapping_hook_text, '<per-user after-mapping-hook>', 'exec')
                extended_attributes = extension_config.get_list('extended_attributes')

                # declaration of extended dashboard groups: this is needed for two reasons:
                # 1. it allows validation of group names, and matching them to dashboard groups
                # 2. it allows removal of dashboard groups not assigned by the hook
                for extended_dashboard_group in extension_config.get_list('extended_dashboard_groups'):
                    group = user_sync.rules.DashboardGroup.create(extended_dashboard_group)
                    if group is None:
                        validation_message = 'Bad dashboard group: "%s" in extension with context "%s"' % (extended_dashboard_group, context)
                        raise user_sync.error.AssertionException(validation_message)

        options = self.options
        result = {
            # these are in alphabetical order!  Always add new ones that way!
            'after_mapping_hook': after_mapping_hook,
            'default_country_code': default_country_code,
            'delete_list_output_path': options['delete_list_output_path'],
            'delete_nonexistent_users': options['delete_nonexistent_users'],
            'delete_user_key_list': options['delete_user_key_list'],
            'directory_group_filter': options['directory_group_filter'],
            'directory_group_mapped': options['directory_group_mapped'],
            'exclude_groups': exclude_groups,
            'exclude_identity_types': exclude_identity_types,
            'exclude_users': exclude_users,
            'extended_attributes': extended_attributes,
            'manage_groups': options['manage_groups'],
            'max_deletions_per_run': max_deletions_per_run,
            'max_missing_users': max_missing_users,
            'new_account_type': new_account_type,
            'remove_list_output_path': options['remove_list_output_path'],
            'remove_nonexistent_users': options['remove_nonexistent_users'],
            'remove_user_key_list': options['remove_user_key_list'],
            'update_user_info': options['update_user_info'],
            'username_filter_regex': options['username_filter_regex'],
        }
        return result

    def create_dashboard_options(self, config_filename, additional_connector_config_sources, owner):
        '''
        load dashboard configuration given config filename, and optionally
        any additional configuration sources.
        :type config_filename: str
        :type additional_connector_config_sources: list(str or dict)
        '''
        # load all additional configuration sources and merge them
        additional_connector_configs = [self.get_dict_from_sources(additional_connector_config_sources, owner)]
        
        # create ConfigFileLoader object and merge with additional sources
        connector_config = ConfigFileLoader(config_filename)
        connector_config.merge_with_dict(additional_connector_configs)

        # process enterprise configuration
        enterprise_section = connector_config.content.get('enterprise')
        if (isinstance(enterprise_section, dict)):
            org_id = enterprise_section.get('org_id')
            if (org_id != None):                    
                credential_config_source = credential_manager.get_credentials(credential_manager.UMAPI_CREDENTIAL_TYPE, org_id, config = enterprise_section, config_loader = self)
                new_enterprise_section = self.get_dict_from_sources([enterprise_section, credential_config_source], "dashboard_credential_manager[%s]" % org_id)
                connector_config.content['enterprise'] = new_enterprise_section

        return connector_config

    def check_unused_config_keys(self):
        directory_connectors_config = self.get_directory_connector_configs()
        self.main_config.report_unused_values(self.logger, [directory_connectors_config])
        
        directory_source_filters = self.options['directory_source_filters']
        if (directory_source_filters != None):
            unused_keys = set(directory_source_filters.iterkeys()) - self.directory_source_filters_accessed
            if (len(unused_keys) > 0):
                raise user_sync.error.AssertionException("Unused source filters for: %s" % list(unused_keys))
        
# base class for configuration tree
class ObjectConfig(object):
    def __init__(self, scope):
        '''
        :type scope: str
        '''
        self.parent = None        
        self.child_configs = {}
        self.scope = scope
    
    def set_parent(self, parent):
        self.parent = parent
    
    def add_child(self, config):
        '''
        :type config: ObjectConfig 
        '''
        config.set_parent(self)
        self.child_configs[config.scope] = config
        
    def find_child_config(self, scope):
        '''
        returns a child given the scope
        :scope: str
        :rtype: any
        '''
        return self.child_configs.get(scope)
    
    def iter_configs(self):
        '''
        :rtype iterable(ObjectConfig)
        '''
        yield self        
        for child_config in self.child_configs.itervalues():
            for subtree_config in child_config.iter_configs():
                yield subtree_config
                
    def get_full_scope(self):
        scopes = []
        config = self
        while (config != None):
            scopes.insert(0, str(config.scope))
            config = config.parent
        return '.'.join(scopes)
    
    def create_assertion_error(self, message):
        return user_sync.error.AssertionException("%s in: %s" % (message, self.get_full_scope()))
    
    def describe_types(self, types_to_describe):
        if (types_to_describe == types.StringTypes):
            result = self.describe_types(types.StringType)
        elif (isinstance(types_to_describe, tuple)):
            result = []
            for type_to_describe in types_to_describe:
                result.extend(self.describe_types(type_to_describe))
        else:
            result = [types_to_describe.__name__]
        return result
    
    def report_unused_values(self, logger, optional_configs = []):
        has_error = False        
        for config in self.iter_configs():
            messages = config.describe_unused_values()
            if (len(messages) > 0):
                if (config in optional_configs):
                    log_level = logging.WARNING
                else:
                    log_level = logging.ERROR
                    has_error = True
                for message in messages:
                    logger.log(log_level, message)
        
        if (has_error):
            raise user_sync.error.AssertionException('Detected unused keys that are not ignorable.')
    
    def describe_unused_values(self):
        return []
        

class ListConfig(ObjectConfig):    
    def __init__(self, scope, value):
        '''
        :type scope: str
        :type value: list
        '''
        super(ListConfig, self).__init__(scope)
        self.value = value
        
    def iter_values(self, allowed_types):
        '''
        :type allowed_types
        '''
        index = 0
        for item in self.value:
            if (not isinstance(item, allowed_types)):
                reported_types = self.describe_types(allowed_types)
                raise self.create_assertion_error("Value should be one of these types: %s for index: %s" % (reported_types, index))
            index += 1
            yield item

    def iter_dict_configs(self):
        index = 0
        for value in self.iter_values(dict):
            config = self.find_child_config(index)
            if (config == None):
                config = DictConfig("[%s]" % index, value)
                self.add_child(config)
            yield config
            index += 1
            
    
class DictConfig(ObjectConfig):
    def __init__(self, scope, value):
        '''
        
        :type scope: str
        :type value: dict
        '''
        super(DictConfig, self).__init__(scope)
        self.value = value
        self.accessed_keys = set()
        
    def has_key(self, key):
        return key in self.value
    
    def iter_keys(self):
        return self.value.iterkeys()
    
    def iter_unused_keys(self):
        for key in self.iter_keys():
            if (key not in self.accessed_keys):
                yield key
        
    def get_dict_config(self, key, none_allowed = False):
        '''
        returns a 
        :key: str
        :rtype DictConfig
        '''
        # check the child configurations for the key
        result = self.find_child_config(key)
        if not result:
            # check the config value for the key. If the value is found, add
            # it to the child configuration collection
            value = self.get_dict(key, none_allowed)
            if value:
                result = DictConfig(key, value)
                self.add_child(result)
        return result        

    def get_dict(self, key, none_allowed = False):
        value = self.get_value(key, dict, none_allowed)
        return value

    def get_string(self, key, none_allowed = False):
        return self.get_value(key, types.StringTypes, none_allowed)

    def get_int(self, key, none_allowed = False):
        return self.get_value(key, types.IntType, none_allowed)

    def get_bool(self, key, none_allowed = False):
        return self.get_value(key, types.BooleanType, none_allowed)

    def get_list(self, key, none_allowed = False):        
        value = self.get_value(key, None, none_allowed)
        if (value != None and not isinstance(value, list)):
            value = [value]
        return value

    def get_list_config(self, key, none_allowed = False):
        '''
        :rtype ListConfig
        '''
        # try to get the child configuration given the key
        result = self.find_child_config(key)
        
        # if the configuration doesn't exist, look in the dictionary value for
        # the # value mapped to the key, and add it to the child map
        if not result:
            value = self.get_list(key, none_allowed)
            if value:
                result = ListConfig(key, value)
                self.add_child(result)
                
        return result
    
    def get_value(self, key, allowed_types, none_allowed = False):
        '''
        validates and returns the value mapped to the specified key.
        :type key: str
        :type allowed_types
        :type none_allowed: bool
        '''
        self.accessed_keys.add(key)
        
        # try to get the value mapped to the key
        result = self.value.get(key)
        if result == None:
            # if none is not allowed, raise the exception
            if not none_allowed:
                raise self.create_assertion_error("Value not found for key: %s" % key)
            
        # if the value is not an instance of an allowed type, raise this
        # exception
        elif allowed_types and not isinstance(result, allowed_types):
            reported_types = self.describe_types(allowed_types)
            raise self.create_assertion_error("Value should be one of these types: %s for key: %s" % (reported_types, key))
        
        return result
    
    def describe_unused_values(self):
        messages = []
        unused_keys = list(self.iter_unused_keys())
        if (len(unused_keys) > 0):
            messages.append("Found unused keys: %s in: %s" % (unused_keys, self.get_full_scope()))
        return messages

def load_from_yaml(filename):
    '''
    loads a yaml file and returns it as a dict.
    :type filename: str
    '''        
    try:
        with open(filename, 'r', 1) as input_file:
            return yaml.load(input_file)
    except IOError as e:
        # if a file operation error occurred while loading the
        # configuration file, swallow up the exception and re-raise this
        # as an configuration loader exception.
        raise user_sync.error.AssertionException('Error reading configuration file: %s' % e)
    except yaml.error.MarkedYAMLError as e:
        # same as above, but indicate this problem has to do with
        # parsing the configuration file.
        raise user_sync.error.AssertionException('Error parsing configuration file: %s' % e)

def combine_dicts(dicts):        
    '''
    Return a single dict from an iterable of dicts. Each dict is merged into
    the resulting dict, with a latter dict possibly overwriting the keys
    from previous dicts.
    :type dicts: list(dict)
    :rtype dict
    '''
    result = {}
    for dict_item in dicts:
        if (isinstance(dict_item, dict)):
            for dict_key, dict_item in dict_item.iteritems():
                result_item = result.get(dict_key)
                if (isinstance(result_item, dict) and isinstance(dict_item, dict)):
                    result_item.update(dict_item)
                else:
                    result[dict_key] = dict_item
    return result

class ConfigFileLoader(object):
    def __init__(self, filename):
        '''
        loads a configuration from a yaml file, and retains the directory
        context
        :type filename: str
        :type content: dict
        '''
        self.filename = filename
        self.dirpath = os.path.dirname(filename)
        self.content = load_from_yaml(filename)
        
    def load_config(self, filename):
        '''
        load a filename relative to this configuration's directory context
        :type filename: str
        :rtype ConfigFileLoader
        '''
        return ConfigFileLoader(self.get_relative_filename(filename))
        
    def get_relative_filename(self, filename):
        '''
        returns a filename relative to this configuration's directory context
        :type filename: str
        :rtype str
        '''
        # if the filename is not absolute, process the relative path
        if not os.path.isabs(filename):
            # if the configuration directory context is set, apply it to the
            # given filename
            if self.dirpath:
                filename = self.dirpath + '/' + filename
            
        return filename
        
    def merge_with_dict(self, dicts):
        '''
        merges the contents of this ConfigFileLoader with the specified dict,
        and stores the resulting dict as the new content for this
        ConfigFileLoader
        :type dicts: list(dict)
        '''
        # prepend content to list of dicts, so old values will be overwritten
        # with new values if they share the same key
        dicts.insert(0, self.content)
        self.content = combine_dicts(dicts)
        
    
class OptionsBuilder(object):
    def __init__(self, default_config):
        '''
        :type default_config: DictConfig
        '''
        self.default_config = default_config
        self.options = {}
        
    def get_options(self):
        return self.options
    
    def set_bool_value(self, key, default_value):
        '''
        :type key: str
        :type default_value: bool
        '''
        self.set_value(key, types.BooleanType, default_value)

    def set_int_value(self, key, default_value):
        '''
        :type key: str
        :type default_value: int
        '''
        self.set_value(key, types.IntType, default_value)

    def set_string_value(self, key, default_value):
        '''
        :type key: str
        :type default_value: str
        '''
        self.set_value(key, types.StringTypes, default_value)

    def set_dict_value(self, key, default_value):
        '''
        :type key: str
        :type default_value: dict
        '''
        self.set_value(key, dict, default_value)
    
    def set_value(self, key, allowed_types, default_value):
        '''
        :type key: str
        '''
        value = default_value
        config = self.default_config
        if (config != None and config.has_key(key)):            
            value = config.get_value(key, allowed_types, False)
        self.options[key] = value

    def require_string_value(self, key):
        '''
        :type key: str
        :rtype str
        '''
        return self.require_value(key, types.StringTypes)
        
    def require_value(self, key, allowed_types):
        '''
        :type key: str
        '''
        config = self.default_config
        if (config == None):
            raise user_sync.error.AssertionException("No config found.")
        self.options[key] = value = config.get_value(key, allowed_types)
        return value
