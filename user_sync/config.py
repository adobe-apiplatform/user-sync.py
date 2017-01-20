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

DEFAULT_CONFIG_DIRECTORY = ''
DEFAULT_MAIN_CONFIG_FILENAME = 'user-sync-config.yml'
DEFAULT_DASHBOARD_OWNING_CONFIG_FILENAME = 'dashboard-owning-config.yml'
DEFAULT_DASHBOARD_TRUSTEE_CONFIG_FILENAME_FORMAT = 'dashboard-trustee-{organization_name}-config.yml'

GROUP_NAME_DELIMITER = '::'

class ConfigLoader(object):
    def __init__(self, caller_options):
        '''
        :type caller_options: dict
        '''        
        self.options = options = {
            'config_directory': DEFAULT_CONFIG_DIRECTORY,
            'main_config_filename': DEFAULT_MAIN_CONFIG_FILENAME,            

            'directory_connector_module_name': None,
            'directory_connector_overridden_options': None,
            'directory_group_filter': None,
            'username_filter_regex': None,
            'directory_source_filters': None,

            'test_mode': False,            
            'manage_groups': True,
            'update_user_info': True,
            
            'remove_user_key_list': None,
            'remove_list_output_path': None,
            'remove_nonexistent_users': False
        }
        options.update(caller_options)     

        main_config_filename = options.get('main_config_filename')
        self.main_config_path = main_config_path = self.get_file_path(main_config_filename)
        
        if (not os.path.isfile(main_config_path)):
            raise user_sync.error.AssertionException('Config file does not exist: %s' % (main_config_path))  
        
        self.directory_source_filters_accessed = set()        
        
        self.logger = logger = logging.getLogger('config')
        logger.info("Using main config file: %s", main_config_path)                
        config_content = self.load_from_yaml(self.main_config_path)         
        self.main_config = DictConfig("<%s>" % main_config_filename, config_content)
        
    def set_options(self, caller_options):          
        '''
        :type caller_options: dict
        '''
        self.options.update(caller_options)        
        
    def get_logging_config(self):
        return self.main_config.get_dict_config('logging', True)

    def get_dashboard_options_for_owning(self):
        owning_config_filename = DEFAULT_DASHBOARD_OWNING_CONFIG_FILENAME
        owning_config_path = self.get_file_path(owning_config_filename)
        
        owning_config = None
        dashboard_config = self.main_config.get_dict_config('dashboard', True)
        if (dashboard_config != None):
            owning_config = dashboard_config.get_list('owning', True)
        owning_config_sources = self.as_list(owning_config)
        if (os.path.isfile(owning_config_path)):
            owning_config_sources.append(owning_config_filename)
        owning_config_sources.append({
            'test_mode': self.options['test_mode']
        })
        return self.create_dashboard_options(owning_config_sources, 'owning_dashboard') 
    
    def get_dashboard_options_for_trustees(self):
        dashboard_config = self.main_config.get_dict_config('dashboard', True)

        trustee_config_filename_format = None        
        if (dashboard_config != None):
            trustee_config_filename_format = dashboard_config.get_string('trustee_config_filename_format', True)                        
        if (trustee_config_filename_format == None):
            trustee_config_filename_format = DEFAULT_DASHBOARD_TRUSTEE_CONFIG_FILENAME_FORMAT
            
        trustee_config_file_paths = {}
        trustee_config_filename_wildcard = trustee_config_filename_format.format(**{'organization_name': '*'})
        for file_path in glob.glob1(self.options.get('config_directory'), trustee_config_filename_wildcard):
            parse_result = self.parse_string(trustee_config_filename_format, file_path)
            organization_name = parse_result.get('organization_name')
            if (organization_name != None):
                trustee_config_file_paths[organization_name] = file_path
             
        trustees_config = None
        if (dashboard_config != None):
            trustees_config = dashboard_config.get_dict_config('trustees', True)
                
        trustees_options = {}
        organization_names = set(trustee_config_file_paths.iterkeys())
        if (trustees_config != None):
            organization_names.update(trustees_config.iter_keys())
        for organization_name in organization_names:
            trustee_config = None
            if (trustees_config != None): 
                trustee_config = trustees_config.get_list(organization_name, True) 
            trustee_config_sources = self.as_list(trustee_config)
            trustee_config_file_path = trustee_config_file_paths.get(organization_name, None)
            if (trustee_config_file_path != None):
                trustee_config_sources.append(trustee_config_file_path)
            trustee_config_sources.append({            
                'test_mode': self.options['test_mode']
            })
            trustees_options[organization_name] = self.create_dashboard_options(trustee_config_sources, 'trustee_dashboard[%s]' % organization_name)
        return trustees_options
    
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
        :rtype dict(str, list(user_sync.rules.Group))
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
            if (groups == None):
                adobe_groups_by_directory_group[directory_group] = groups = []

            dashboard_groups_config = item.get_list_config('dashboard_groups')
            for dashboard_group in dashboard_groups_config.iter_values(types.StringTypes):
                parts = dashboard_group.split(GROUP_NAME_DELIMITER)
                group_name = parts.pop()
                organization_name = GROUP_NAME_DELIMITER.join(parts)
                if (len(organization_name) == 0):
                    organization_name = user_sync.rules.OWNING_ORGANIZATION_NAME
                if (len(group_name) == 0):
                    validation_message = 'Bad dashboard group: "%s" in directory group: "%s"' % (dashboard_group, directory_group)
                    raise user_sync.error.AssertionException(validation_message)                    
                group = user_sync.rules.Group(group_name, organization_name)
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
            if (isinstance(source, types.StringTypes)):
                absolute_path = self.get_absolute_file_path(source)
                if (os.path.isfile(absolute_path)):
                    config = self.load_from_yaml(absolute_path)
                    options.append(config)
                else:
                    raise user_sync.error.AssertionException('Cannot find file: %s for: %s' % (absolute_path, owner))
            elif (isinstance(source, dict)):
                options.append(source)
            elif (source != None):
                raise user_sync.error.AssertionException('Source should be a filename or a dictionary for: %s' % owner)
        return self.combine_dicts(options)
    
    def get_absolute_file_path(self, value):
        '''
        If value is an absolute path, return as is.  Otherwise, if value is a relative path, 
        make sure the path is relative from the config path.
        :type value: str
        '''        
        path = value if os.path.isabs(value) else self.get_file_path(value)
        return path
    
    def load_from_yaml(self, file_path):
        '''
        :type file_path: str
        '''        
        with open(file_path, 'r', 1) as input_file:
            return yaml.load(input_file)
        
    def get_file_path(self, filename):
        '''
        :type filename: str
        :rtype str
        '''        
        directory = self.options.get('config_directory')
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
        new_account_type = None
        default_country_code = None
        directory_config = self.main_config.get_dict_config('directory', True)
        if (directory_config != None): 
            new_account_type = directory_config.get_string('user_identity_type', True)
            new_account_type = user_sync.identity_type.parse_identity_type(new_account_type)
            default_country_code = directory_config.get_string('default_country_code', True)
        if (new_account_type == None):
            new_account_type = user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE
            self.logger.warning("Assuming the identity type for users is: %s", new_account_type)
        
        options = self.options
        result = {
            'directory_group_filter': options['directory_group_filter'],
            'username_filter_regex': options['username_filter_regex'],
            'new_account_type': new_account_type,
            'manage_groups': options['manage_groups'],
            'update_user_info': options['update_user_info'],
            'remove_user_key_list': options['remove_user_key_list'],
            'remove_list_output_path': options['remove_list_output_path'],
            'remove_nonexistent_users': options['remove_nonexistent_users'],
            'default_country_code': default_country_code
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
