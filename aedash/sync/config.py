import os
import yaml
import types

import rules

DEFAULT_CONFIG_DIRECTORY = ''
DEFAULT_MAIN_CONFIG_FILENAME = 'user-sync-config.yml'

class ConfigLoader(object):
    def __init__(self, caller_options):
        '''
        :type caller_options: dict
        '''        
        self.options = options = {
            'directory': DEFAULT_CONFIG_DIRECTORY,
            'main_config_filename': DEFAULT_MAIN_CONFIG_FILENAME
        }
        options.update(caller_options)     

        main_config_filename = options.get('main_config_filename')
        self.main_config_path = main_config_path = self.get_file_path(main_config_filename)
        
        if (not os.path.isfile(main_config_path)):
            raise Exception('Config file does not exist: %s' % (main_config_path))  
        
        self.config_cache = {}          
        
    def get_main_config(self):
        return self.get_config(None, self.load_main_config)
    
    def load_main_config(self):
        return self.load_from_yaml(self.main_config_path) 
    
    def get_logging_config(self):
        main_config = self.get_main_config()
        return main_config.get('logging', {})
    
    def get_directory_config(self):
        return self.get_config('directory', self.load_directory_config)
    
    def load_directory_config(self):
        main_config = self.get_main_config()
        directory_config = main_config.get('directory', {})
        
        connectors_config = directory_config.get('connectors')        
        directory_config['connectors'] = new_connectors_config = {}                
        if (isinstance(connectors_config, dict)):
            for key, item in connectors_config.iteritems():
                if (isinstance(item, types.StringTypes)):
                    path = item if os.path.isabs(item) else self.get_file_path(item)
                    new_item = self.load_from_yaml(path)
                else:
                    new_item = item
                new_connectors_config[key] = new_item
                
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
                        new_groups_config[directory_group] = products = []
                        for adobe_group in adobe_groups:
                            parts = adobe_group.split(':')
                            product_name = parts.pop()
                            organization_name = ':'.join(parts)
                            if (len(organization_name) == 0):
                                organization_name = None
                            product = rules.Product(product_name, organization_name)
                            products.append(product)
        
        return directory_config

    def get_config(self, key, factory_method):
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
        directory = self.options.get('directory')
        path = os.path.join(directory, filename)
        return path
