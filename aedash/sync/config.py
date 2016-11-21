import glob
import os
import re
import types
import yaml

from aedash.sync import credential_manager
import aedash.sync.error
import aedash.sync.rules

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

            'directory_connector_module_name': 'aedash.sync.connector.directory_ldap',
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
            raise aedash.sync.error.AssertionException('Config file does not exist: %s' % (main_config_path))  
        
        self.config_cache = {}
        
    def set_options(self, caller_options):          
        '''
        :type caller_options: dict
        '''
        self.options.update(caller_options)        
        
    def get_main_config(self):
        return self.get_config(None, self.load_main_config)
    
    def load_main_config(self):
        return self.load_from_yaml(self.main_config_path) 
    
    def get_logging_config(self):
        return self.get_config_section('logging')

    def get_dashboard_config(self):
        return self.get_config('dashboard', self.load_dashboard_config)
    
    def get_config_section(self, name):
        main_config = self.get_main_config()
        section = main_config.get(name, None)
        if (not isinstance(section, dict)):
            section = {}
        return section
    
    def load_dashboard_config(self):
        dashboard_config = self.get_config_section('dashboard') 

        owning_config_filename = dashboard_config.get('owning_config_filename', DEFAULT_DASHBOARD_OWNING_CONFIG_FILENAME)
        trustee_config_filename_format = dashboard_config.get('trustee_config_filename_format', DEFAULT_DASHBOARD_TRUSTEE_CONFIG_FILENAME_FORMAT)
        
        trustee_config_file_paths = {}
        trustee_config_filename_wildcard = trustee_config_filename_format.format(**{'organization_name': '*'})
        for file_path in glob.glob1(self.options.get('config_directory'), trustee_config_filename_wildcard):
            parse_result = self.parse_string(trustee_config_filename_format, file_path)
            organization_name = parse_result.get('organization_name')
            if (organization_name != None):
                trustee_config_file_paths[organization_name] = file_path
             
        owning_config = dashboard_config.get('owning', {})
        owning_config_sources = self.get_config_sources(owning_config)
        if (os.path.isfile(owning_config_filename)):
            owning_config_sources.append(owning_config_filename)
        owning_config_sources.append({
            'test_mode': self.options['test_mode'],
            'logger_name': 'dashboard.owning'
        })
        dashboard_config['owning'] = self.create_dashboard_connector_config(owning_config_sources, 'owning_dashboard') 
        
        trustees_config = dashboard_config.get('trustees')
        if (not isinstance(trustees_config, dict)):
            trustees_config = {}
        
        dashboard_config['trustees'] = new_trustees_config = {}
        organization_names = set()
        organization_names.update(trustees_config.iterkeys(), trustee_config_file_paths.iterkeys())
        for organization_name in organization_names:
            trustee_config = trustees_config.get(organization_name)
            trustee_config_sources = self.get_config_sources(trustee_config) if trustee_config != None else []
            trustee_config_file_path = trustee_config_file_paths.get(organization_name, None)
            if (trustee_config_file_path != None):
                trustee_config_sources.append(trustee_config_file_path)
            trustee_config_sources.append({            
                'test_mode': self.options['test_mode'],
                'logger_name': 'dashboard.trustee.%s' % organization_name
            })
            new_trustees_config[organization_name] = self.create_dashboard_connector_config(trustee_config_sources, 'trustee_dashboard[%s]' % organization_name)
        
        return dashboard_config
    
    def get_directory_config(self):
        return self.get_config('directory', self.load_directory_config)
    
    def load_directory_config(self):
        options = self.options
        directory_source_filters = options['directory_source_filters']
        
        directory_config = self.get_config_section('directory') 
        
        connectors_config = directory_config.get('connectors')        
        directory_config['connectors'] = new_connectors_config = {}                
        if (isinstance(connectors_config, dict)):
            for key, item in connectors_config.iteritems():
                config_sources = self.get_config_sources(item)
                new_connectors_config[key] = self.get_dict_config(config_sources, 'directory[%s]' % key)
                
        connector_names = set(new_connectors_config.iterkeys())
        if (directory_source_filters != None):
            connector_names.union(directory_source_filters.iterkeys())
        for connector_name in connector_names:
            source_filter_sources = []
            connector_config = new_connectors_config.get(connector_name)
            if (connector_config != None):
                source_filter_sources.append(connector_config.get('source_filter'))
            else:
                new_connectors_config[connector_name] = connector_config = {}
            if (directory_source_filters != None):
                source_filter_sources.append(directory_source_filters.get(connector_name))
            connector_config['source_filters'] = self.get_dict_config(source_filter_sources, 'directory[%s].source_filters' % key)
                
        groups_config = directory_config.get('groups')
        directory_config['groups'] = new_groups_config = {}                
        if (isinstance(groups_config, list)):
            for item in groups_config:
                if (isinstance(item, dict)):
                    directory_group = item.get('directory_group')
                    adobe_groups = item.get('dashboard_groups')
                    if isinstance(adobe_groups, types.StringTypes):
                        adobe_groups = [adobe_groups]
                    elif not isinstance(adobe_groups, list):
                        adobe_groups = None    
                    if (directory_group == None):
                        pass
                    elif (adobe_groups == None or len(adobe_groups) == 0):
                        pass
                    else:
                        groups = new_groups_config.get(directory_group)
                        if (groups == None):
                            new_groups_config[directory_group] = groups = []
                        for adobe_group in adobe_groups:
                            parts = adobe_group.split(GROUP_NAME_DELIMITER)
                            group_name = parts.pop()
                            organization_name = GROUP_NAME_DELIMITER.join(parts)
                            if (len(organization_name) == 0):
                                organization_name = aedash.sync.rules.OWNING_ORGANIZATION_NAME
                            if (len(group_name) > 0):
                                group = aedash.sync.rules.Group(group_name, organization_name)
                                groups.append(group)
        
        return directory_config
    
    def get_directory_connector_module_name(self):
        '''
        :rtype str
        '''
        options = self.options
        return options['directory_connector_module_name']
    
    def get_directory_connector_config(self, connector_name):
        '''
        :rtype dict
        '''
        configs = []        
        directory_config = self.get_directory_config()        
        configs.append(directory_config['connectors'].get(connector_name))
        configs.append(self.options['directory_connector_overridden_options'])
        
        result = self.combine_dicts(configs)
        credential_config = credential_manager.get_credentials(credential_manager.DIRECTORY_CREDENTIAL_TYPE, connector_name, config = result, config_loader = self)
        if (isinstance(credential_config, dict)):
            result.update(credential_config)
        return result
    
    def get_directory_groups(self):
        '''
        :rtype dict(str, list(aedash.sync.rules.Group))
        '''
        directory_config = self.get_directory_config()
        return directory_config['groups']        
        
    def get_config_sources(self, value):
        values = value if (isinstance(value, types.ListType)) else [value]
        return values
        
    def get_configs(self, sources, owner):
        '''
        :type sources: list
        '''        
        configs = []
        for source in sources: 
            if (isinstance(source, types.StringTypes)):
                absolute_path = self.get_absolute_file_path(source)
                if (os.path.isfile(absolute_path)):
                    config = self.load_from_yaml(absolute_path)
                    configs.append(config)
                else:
                    raise aedash.sync.error.AssertionException('Cannot find file: %s for: %s' % (absolute_path, owner))
            else:
                configs.append(source)
        return configs
    
    def get_dict_config(self, sources, owner):
        '''
        :type sources: list
        '''        
        configs = self.get_configs(sources, owner)
        return self.combine_dicts(configs)

    def get_absolute_file_path(self, value):
        '''
        :type value: str
        '''        
        path = value if os.path.isabs(value) else self.get_file_path(value)
        return path
    
    def get_config(self, key, factory_method):
        '''
        :type key: str
        :type factory_method: callable
        '''        
        config = self.config_cache.get(key)
        if (config == None):
            config = factory_method()
            self.config_cache[key] = config
        return config 
    
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

    def get_rule_config(self):
        options = self.options
        result = {
            'directory_group_filter': options['directory_group_filter'],
            'username_filter_regex': options['username_filter_regex'],
            'new_account_type': self.get_new_account_type(),
            'manage_groups': options['manage_groups'],
            'update_user_info': options['update_user_info'],
            'remove_user_key_list': options['remove_user_key_list'],
            'remove_list_output_path': options['remove_list_output_path'],
            'remove_nonexistent_users': options['remove_nonexistent_users']

        }
        return result

    def get_new_account_type(self):
        directory_config = self.get_config_section('directory') 
        new_account_type = directory_config.get('type')
        if (new_account_type == None):
            new_account_type = aedash.sync.rules.ENTERPRISE_IDENTITY_TYPE
        return new_account_type

    def create_dashboard_connector_config(self, connector_config_sources, owner):
        connector_config = self.get_dict_config(connector_config_sources, owner)
        enterprise_section = connector_config.get('enterprise')
        if (isinstance(enterprise_section, dict)):
            org_id = enterprise_section.get('org_id')
            if (org_id != None):                    
                credential_config = credential_manager.get_credentials(credential_manager.UMAPI_CREDENTIAL_TYPE, org_id, config = enterprise_section, config_loader = self)
                if (isinstance(credential_config, dict)):
                    enterprise_section.update(credential_config)
        return connector_config
