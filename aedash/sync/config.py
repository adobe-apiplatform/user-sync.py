import os
import yaml

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
        
    def load_main_config(self):
        return self.load_from_yaml(self.main_config_path)   
    
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
        

if __name__ == '__main__':
    c = os.path.join('', 'david')
    
    a = 0