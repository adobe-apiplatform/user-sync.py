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

# list of key paths in the root configuration file that will be processed as
# filenames relative to the configuration's file path
ROOT_CONFIG_PATH_KEYS = [
        { 'path':'/dashboard/owning', 'default': DEFAULT_DASHBOARD_OWNING_CONFIG_FILENAME },
        '/dashboard/owning/enterprise/priv_key_path',
        '/dashboard/accessors/*',
        '/dashboard/accessors/*/enterprise/priv_key_path',
        { 'path':'/dashboard/accessor_config_filename_format', 'default':DEFAULT_DASHBOARD_ACCESSOR_CONFIG_FILENAME_FORMAT },
        '/directory/connectors/ldap',
        '/logging/file_log_directory'
    ]

# like ROOT_CONFIG_PATH_KEYS, but this is applied to non-root configuration
# files
SUB_CONFIG_PATH_KEYS = [
        "/enterprise/priv_key_path"
    ]

class ConfigLoader(object):
    def __init__(self, caller_options):
        '''
        :type caller_options: dict
        '''        
        self.options = options = {
            # these are in alphabetical order!  Always add new ones that way!
            'delete_strays': False,
            'directory_connector_module_name': None,
            'directory_connector_overridden_options': None,
            'directory_group_filter': None,
            'directory_group_mapped': False,
            'directory_source_filters': None,
            'disentitle_strays': False,
            'main_config_filename': DEFAULT_MAIN_CONFIG_FILENAME,
            'manage_groups': False,
            'remove_strays': False,
            'stray_key_list': None,
            'stray_list_output_path': None,
            'test_mode': False,
            'update_user_info': True,
            'username_filter_regex': None,
        }
        options.update(caller_options)     

        main_config_filename = options.get('main_config_filename')
        main_config_content = ConfigFileLoader.load_root_config(main_config_filename)
        
        if (not os.path.isfile(main_config_filename)):
            raise user_sync.error.AssertionException('Config file does not exist: %s' % (main_config_filename))  
        
        self.directory_source_filters_accessed = set()        
        
        self.logger = logger = logging.getLogger('config')
        logger.info("Using main config file: %s", main_config_filename)                
        self.main_config = DictConfig("<%s>" % main_config_filename, main_config_content)
        
    def set_options(self, caller_options):          
        '''
        :type caller_options: dict
        '''
        self.options.update(caller_options)        
        
    def get_logging_config(self):
        return self.main_config.get_dict_config('logging', True)

    def get_dashboard_options_for_owning(self):
        owning_config = None
        dashboard_config = self.main_config.get_dict_config('dashboard', True)
        if (dashboard_config != None):
            owning_config = dashboard_config.get_list('owning', True)
        owning_config_sources = self.as_list(owning_config)
        owning_config_sources.append({
            'test_mode': self.options['test_mode']
        })
        return self.create_dashboard_options(owning_config_sources, 'owning_dashboard') 
    
    def get_dashboard_options_for_accessors(self):
        dashboard_config = self.main_config.get_dict_config('dashboard', True)

        accessor_config_filename_format = None        
        if (dashboard_config != None):
            accessor_config_filename_format = dashboard_config.get_string('accessor_config_filename_format', True)                        
        if (accessor_config_filename_format == None):
            accessor_config_filename_format = DEFAULT_DASHBOARD_ACCESSOR_CONFIG_FILENAME_FORMAT
            
        accessor_config_file_paths = {}
        accessor_config_filename_wildcard = accessor_config_filename_format.format(**{'organization_name': '*'})
        for file_path in glob.glob(accessor_config_filename_wildcard):
            parse_result = self.parse_string(accessor_config_filename_format, file_path)
            organization_name = parse_result.get('organization_name')
            if (organization_name != None):
                accessor_config_file_paths[organization_name] = file_path
             
        accessors_config = None
        if (dashboard_config != None):
            accessors_config = dashboard_config.get_dict_config('accessors', True)
                
        accessors_options = {}
        organization_names = set(accessor_config_file_paths.iterkeys())
        if (accessors_config != None):
            organization_names.update(accessors_config.iter_keys())
        for organization_name in organization_names:
            accessor_config = None
            if (accessors_config != None): 
                accessor_config = accessors_config.get_list(organization_name, True) 
            accessor_config_sources = self.as_list(accessor_config)
            accessor_config_file_path = accessor_config_file_paths.get(organization_name, None)
            if (accessor_config_file_path != None):
                accessor_config_sources.append(accessor_config_file_path)
            accessor_config_sources.append({            
                'test_mode': self.options['test_mode']
            })
            accessors_options[organization_name] = self.create_dashboard_options(accessor_config_sources, 'accessor_dashboard[%s]' % organization_name)
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
        connectors_config = self.get_directory_connector_configs()
        if (connectors_config != None):
            connector_item = connectors_config.get_list(connector_name, True)
            connector_options = self.get_dict_from_sources(connector_item, 'directory[%s]' % connector_name)
        
        source_filter_sources = self.as_list(connector_options.get('source_filter'))
        directory_source_filters = self.options['directory_source_filters']
        if (directory_source_filters != None):
            self.directory_source_filters_accessed.add(connector_name)
            # get the dictionary for the source filter file
            directory_source_list = self.as_list(directory_source_filters.get(connector_name))
            source_filter_dict = self.get_dict_from_sources(directory_source_list,'directory[%s].source_filters' % connector_name)
            # ensure it contains an 'all_users_filter'
            if (source_filter_dict.get('all_users_filter') == None):
                self.logger.warn('Ignoring source filter for directory[%s] as "all_users_filter" was not specified' % connector_name)
            else:
                source_filter_sources.append(directory_source_filters.get(connector_name))
        source_filters =  self.get_dict_from_sources(source_filter_sources, 'directory[%s].source_filters' % connector_name)
        if (len(source_filters) > 0):   
            connector_options['source_filters'] = source_filters
                
        configs = [connector_options, self.options['directory_connector_overridden_options']]
        current_config = self.combine_dicts(configs)
        credential_config_source = credential_manager.get_credentials(credential_manager.DIRECTORY_CREDENTIAL_TYPE, connector_name, config = current_config, config_loader = self)
        return self.get_dict_from_sources([current_config, credential_config_source], "directory_credential_manager")
    
    def get_directory_groups(self):
        '''
        :rtype dict(str, list(user_sync.rules.DashboardGroup))
        '''
        adobe_groups_by_directory_group = {}
        
        groups_config = None
        directory_config = self.main_config.get_dict_config('directory', True)
        if (directory_config != None):
            groups_config = directory_config.get_list_config('groups', True)         
        if (groups_config == None):
            return adobe_groups_by_directory_group
        
        for item in groups_config.iter_dict_configs():
            directory_group = item.get_string('directory_group')            
            groups = adobe_groups_by_directory_group.get(directory_group)
            if groups == None:
                adobe_groups_by_directory_group[directory_group] = groups = []

            dashboard_groups_config = item.get_list_config('dashboard_groups')
            for dashboard_group in dashboard_groups_config.iter_values(types.StringTypes):
                group = user_sync.rules.DashboardGroup.create(dashboard_group)
                if group is None:
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
        :type sources: list
        '''
        if (sources == None):
            return {}
                
        options = []
        for source in sources: 
            if isinstance(source, types.StringTypes):
                if os.path.isfile(source):
                    config = ConfigFileLoader.load_sub_config(source)
                    options.append(config)
                else:
                    raise user_sync.error.AssertionException('Cannot find file: %s for: %s' % (source, owner))
            elif isinstance(source, dict):
                options.append(source)
            elif source:
                raise user_sync.error.AssertionException('Source should be a filename or a dictionary for: %s' % owner)
        return self.combine_dicts(options)
    
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
    
    @staticmethod
    def combine_dicts(dicts):        
        '''
        Return a single dict from an iterable of dicts.  Each dict is merged into the resulting dict, 
        with a latter dict possibly overwriting the keys from previous dicts.
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


    def get_rule_options(self):
        '''
        Return a dict representing options for RuleProcessor.
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

        limits_config = self.main_config.get_dict_config('limits')
        max_strays_hard_limit = limits_config.get_int('max_strays_hard_limit')
        max_strays_to_process = limits_config.get_int('max_strays_to_process')

        after_mapping_hook = None
        extended_attributes = None
        extensions_config = self.main_config.get_list_config('extensions', True)
        if (extensions_config is not None):
            for extension_config in extensions_config.iter_dict_configs():
                context = extension_config.get_string('context')

                if context != 'per-user':
                    self.logger.warning("Unrecognized extension context '%s' ignored", context)
                    continue
                if (after_mapping_hook is not None):
                    self.logger.warning("Duplicate extension context '%s' ignored", context)
                    continue

                after_mapping_hook_text = extension_config.get_string('after_mapping_hook')

                if after_mapping_hook_text is None:
                    self.logger.warning("No valid hook found in extension with context '%s'; extension ignored")
                    continue

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
            'delete_strays': options['delete_strays'],
            'directory_group_filter': options['directory_group_filter'],
            'directory_group_mapped': options['directory_group_mapped'],
            'disentitle_strays': options['disentitle_strays'],
            'exclude_groups': exclude_groups,
            'exclude_identity_types': exclude_identity_types,
            'exclude_users': exclude_users,
            'extended_attributes': extended_attributes,
            'manage_groups': options['manage_groups'],
            'max_strays_hard_limit': max_strays_hard_limit,
            'max_strays_to_process': max_strays_to_process,
            'new_account_type': new_account_type,
            'remove_strays': options['remove_strays'],
            'stray_key_list': options['stray_key_list'],
            'stray_list_output_path': options['stray_list_output_path'],
            'update_user_info': options['update_user_info'],
            'username_filter_regex': options['username_filter_regex'],
        }
        return result

    def create_dashboard_options(self, connector_config_sources, owner):
        connector_config = self.get_dict_from_sources(connector_config_sources, owner)
        enterprise_section = connector_config.get('enterprise')
        if (isinstance(enterprise_section, dict)):
            org_id = enterprise_section.get('org_id')
            if (org_id != None):                    
                credential_config_source = credential_manager.get_credentials(credential_manager.UMAPI_CREDENTIAL_TYPE, org_id, config = enterprise_section, config_loader = self)
                new_enterprise_section = self.get_dict_from_sources([enterprise_section, credential_config_source], "dashboard_credential_manager[%s]" % org_id)
                connector_config['enterprise'] = new_enterprise_section

        return connector_config

    def check_unused_config_keys(self):
        directory_connectors_config = self.get_directory_connector_configs()
        self.main_config.report_unused_values(self.logger, [directory_connectors_config])
        
        directory_source_filters = self.options['directory_source_filters']
        if (directory_source_filters != None):
            unused_keys = set(directory_source_filters.iterkeys()) - self.directory_source_filters_accessed
            if (len(unused_keys) > 0):
                raise user_sync.error.AssertionException("Unused source filters for: %s" % list(unused_keys))
        
    
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
        :rtype DictConfig
        '''
        result = self.find_child_config(key)
        if (result == None):
            value = self.get_dict(key, none_allowed)
            if (value != None):
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
        result = self.find_child_config(key)
        if (result == None):
            value = self.get_list(key, none_allowed)
            if (value != None):
                result = ListConfig(key, value)
                self.add_child(result)
        return result
    
    def get_value(self, key, allowed_types, none_allowed = False):
        '''
        :type key: str
        :type allowed_types
        :type none_allowed: bool
        '''
        self.accessed_keys.add(key)
        result = self.value.get(key)
        if (result == None):
            if (not none_allowed):
                raise self.create_assertion_error("Value not found for key: %s" % key)
        elif (allowed_types != None and not isinstance(result, allowed_types)):
            reported_types = self.describe_types(allowed_types)
            raise self.create_assertion_error("Value should be one of these types: %s for key: %s" % (reported_types, key))
        return result
    
    def describe_unused_values(self):
        messages = []
        unused_keys = list(self.iter_unused_keys())
        if (len(unused_keys) > 0):
            messages.append("Found unused keys: %s in: %s" % (unused_keys, self.get_full_scope()))
        return messages
    
class ConfigFileLoader(object):
    @staticmethod
    def load_from_yaml(filename, path_keys):
        '''
        loads a yaml file, processes the resulting dict to adapt values for keys
        (the path to which is defined in PATH_KEYS) to a value that represents
        a file reference relative to provided source file, and returns the
        processed dict.
        :type filename: str
        :rtype dict
        '''
        try:
            with open(filename, 'r', 1) as input_file:
                yml = yaml.load(input_file)
        except IOError as e:
            # if a file operation error occurred while loading the
            # configuration file, swallow up the exception and re-raise this
            # as an configuration loader exception.
            raise user_sync.error.AssertionException('Error reading configuration file: %s' % e)
        except yaml.error.MarkedYAMLError as e:
            # same as above, but indicate this problem has to do with
            # parsing the configuration file.
            raise user_sync.error.AssertionException('Error parsing configuration file: %s' % e)

        dirpath = os.path.dirname(filename)
    
        def process_path_key(dictionary, keys, level, default_val):
            '''
            this function is used to process a single path key by replacing the
            value for the key that is found into a path relative to the given
            source file, with the assumption that the value is a file reference
            to begin with. It is used recursively to navigate into child
            dictionaries to search the path key.
            type dictionary: dict
            type keys: list
            type level: int
            type default_val: str
            '''
            def relative_path(filename):
                '''
                returns an absolute path that is resolved relative to the source
                filename. The source filename is provided in the parent
                load_from_yaml function, and os.path.abspath is used to return
                the absolute path of the resolved relative path
                type filename: str
                rtype: str
                '''
                if dirpath and not os.path.isabs(filename):
                    return os.path.abspath(os.path.join(dirpath, filename))
                return filename
            
            def process_path_key_value(key):
                '''
                does the relative path processing for a single key of the
                current dictionary
                type key: str
                '''
                if dictionary.has_key(key):
                    val = dictionary[key]
                    if isinstance(val,str):
                        dictionary[key] = relative_path(val)
                    elif isinstance(val,list):
                        vals = []
                        for entry in val:
                            if isinstance(entry, str):
                                vals.append(relative_path(entry))
                            else:
                                vals.append(entry)
                        dictionary[key] = vals

            # end of path key
            if level == len(keys)-1:
                key = keys[level]
                # if a wildcard is specified at this level, that means we
                # should process all keys as path values
                if key == "*":
                    for key in dictionary.keys():
                        process_path_key_value(key)
                elif dictionary.has_key(key):
                    process_path_key_value(key)
                # key was not found, but default value was set, so apply it
                elif default_val:
                    dictionary[key] = relative_path(default_val)
                    
            elif level < len(keys)-1:
                key = keys[level]
                # if a wildcard is specified at this level, this indicates this
                # should select all keys that have dict type values, and recurse
                # into them at the next level
                if key == "*":
                    for key in dictionary.keys():
                        if isinstance(dictionary[key],dict):
                            process_path_key(dictionary[key], keys, level+1, default_val)
                            
                elif dictionary.has_key(key):
                    # if the key refers to adictionary, recurse into it to go
                    # further down the path key
                    if isinstance(dictionary[key],dict):
                        process_path_key(dictionary[key], keys, level+1, default_val)
                        
                # if the key was not found, but a default value is specified,
                # drill down further to set the default value
                elif default_val:
                    dictionary[key] = {}
                    process_path_key(dictionary[key], keys, level+1, default_val)

        for path_key in path_keys:
            if isinstance(path_key, dict):
                keys = path_key['path'].split('/')
                process_path_key(yml, keys, 1, path_key['default'])
            elif isinstance(path_key, str):
                keys = path_key.split('/')
                process_path_key(yml, keys, 1, None)
            
        return yml
    
    @staticmethod
    def load_root_config(filename):
        '''
        loads the specified file as a root configuration file. This basically
        means that on top of loading the file as a yaml file into a dictionary,
        it will apply the ROOT_CONFIG_PATH_KEYS to the dictionary to replace
        the specified paths with absolute path values that are resolved
        relative to the given configuration's filename.
        type filename: str
        rtype dict
        '''
        return ConfigFileLoader.load_from_yaml(filename, ROOT_CONFIG_PATH_KEYS)
        
    @staticmethod
    def load_sub_config(filename):
        '''
        same as load_root_config, but applies SUB_CONFIG_PATH_KEYS to the
        dictionary loaded from the yaml file.
        '''
        return ConfigFileLoader.load_from_yaml(filename, SUB_CONFIG_PATH_KEYS)
    
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
