import helper

class DirectoryConnector(object):    
    def __init__(self, implementation):
        self.implementation = implementation
        
        required_functions = ['connector_metadata', 'connector_initialize']
        for required_function in required_functions:
            if (not hasattr(implementation, required_function)):
                raise Exception('Missing function: %s source: %s' % (required_function, implementation.__file__))            
 
        self.metadata = metadata = implementation.connector_metadata()
        self.name = name = metadata.get('name')
        if (name == None):
            raise Exception('Missing metadata property: %s source: %s' % ('name', implementation.__file__))
      
    def initialize(self, options = {}):      
        '''
        :type options: dict
        '''
        required_options = self.metadata.get('required_options')
        if (required_options != None):
            validation_result, validation_issue = helper.validate_options(options, required_options)
            if not validation_result:
                raise Exception('%s for connector: %s' % (validation_issue, self.metadata['name']))
        self.state = self.implementation.connector_initialize(options)
        
    def iter_users_with_groups(self, groups):
        return self.implementation.connector_iter_users_with_groups(self.state, groups)        

    def get_users_with_groups(self, groups):
        return list(self.iter_users_with_groups(groups))

    def is_existing_username(self, username):
        return self.implementation.connector_is_existing_username(self.state, username)  