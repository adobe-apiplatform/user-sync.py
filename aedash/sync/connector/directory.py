import aedash.sync.error

class DirectoryConnector(object):    
    def __init__(self, implementation):
        self.implementation = implementation
        
        required_functions = ['connector_metadata', 'connector_initialize']
        for required_function in required_functions:
            if (not hasattr(implementation, required_function)):
                raise aedash.sync.error.AssertionException('Missing function: %s source: %s' % (required_function, implementation.__file__))            
 
        self.metadata = metadata = implementation.connector_metadata()
        self.name = name = metadata.get('name')
        if (name == None):
            raise aedash.sync.error.AssertionException('Missing metadata property: %s source: %s' % ('name', implementation.__file__))
      
    def initialize(self, options = {}):      
        '''
        :type options: dict
        '''
        self.state = self.implementation.connector_initialize(options)
        
    def load_users_and_groups(self, groups):
        '''
        :type groups: list(str)
        :rtype (bool, iterable(dict))
        '''
        return self.implementation.connector_load_users_and_groups(self.state, groups)        

