import aedash.sync.config
import aedash.sync.connector.helper
import aedash.sync.error
import aedash.sync.helper
import aedash.sync.identity_type

def connector_metadata():
    metadata = {
        'name': CSVDirectoryConnector.name
    }
    return metadata

def connector_initialize(options):
    '''
    :type options: dict
    '''
    state = CSVDirectoryConnector(options)
    return state

def connector_load_users_and_groups(state, groups):
    '''
    :type state: CSVDirectoryConnector
    :type groups: list(str)
    :rtype (bool, iterable(dict))
    '''
    return state.load_users_and_groups(groups)

class CSVDirectoryConnector(object):
    name = 'csv'
    
    def __init__(self, caller_options):
        caller_config = aedash.sync.config.DictConfig('"%s options"' % CSVDirectoryConnector.name, caller_options)
        builder = aedash.sync.config.OptionsBuilder(caller_config)
        builder.set_string_value('delimiter', None)
        builder.set_string_value('first_name_column_name', 'firstname')
        builder.set_string_value('last_name_column_name', 'lastname')
        builder.set_string_value('email_column_name', 'email')
        builder.set_string_value('country_column_name', 'country')
        builder.set_string_value('groups_column_name', 'groups')
        builder.set_string_value('username_column_name', 'user')
        builder.set_string_value('domain_column_name', 'domain')
        builder.set_string_value('identity_type_column_name', 'type')
        builder.set_string_value('logger_name', 'connector.' + CSVDirectoryConnector.name)
        builder.require_string_value('file_path')
        options = builder.get_options()        

        self.options = options
        self.logger = logger = aedash.sync.connector.helper.create_logger(options)        
        caller_config.report_unused_values(logger)

        logger.debug('Initialized with options: %s', options)            

    def load_users_and_groups(self, groups):
        '''
        :type groups: list(str)
        :rtype (bool, iterable(dict))
        '''        
        options = self.options
        file_path = options['file_path']
        self.logger.info('Reading from: %s', file_path)
        self.users = users = self.read_users(file_path)                        
        self.logger.info('Number of users loaded: %d', len(users))
        return (True, users.itervalues())

    def read_users(self, file_path):
        '''
        :type file_path
        :rtype dict
        '''
        users = {}
        
        options = self.options
        logger = self.logger
        
        recognized_column_names = []
        def get_column_name(key):
            column_name = options[key]
            recognized_column_names.append(column_name)
            return column_name

        email_column_name = get_column_name('email_column_name')
        first_name_column_name = get_column_name('first_name_column_name')
        last_name_column_name = get_column_name('last_name_column_name')
        country_column_name = get_column_name('country_column_name')
        groups_column_name = get_column_name('groups_column_name')
        identity_type_column_name = get_column_name('identity_type_column_name')
        username_column_name = get_column_name('username_column_name')
        domain_column_name = get_column_name('domain_column_name')
        
        line_read = 0
        rows = aedash.sync.helper.iter_csv_rows(file_path, 
                                                delimiter = options['delimiter'], 
                                                recognized_column_names = recognized_column_names, 
                                                logger = logger)
        for row in rows:
            line_read += 1
            email = self.get_column_value(row, email_column_name)
            if (email == None):
                logger.warning('No email found at row: %d', line_read)
                continue;
            
            user = users.get(email)
            if (user == None):
                user = aedash.sync.connector.helper.create_blank_user()
                user['email'] = email
                users[email] = user
            
            first_name = self.get_column_value(row, first_name_column_name)
            if (first_name != None):    
                user['firstname'] = first_name
            else:
                logger.debug('No value firstname for: %s', email)
                
            last_name = self.get_column_value(row, last_name_column_name)
            if (last_name != None):    
                user['lastname'] = last_name
            else:
                logger.debug('No value lastname for: %s', email)
    
            country = self.get_column_value(row, country_column_name)
            if (country != None):    
                user['country'] = country
                
            groups = self.get_column_value(row, groups_column_name)
            if (groups != None):
                user['groups'].extend(groups.split(','))
                
            username = self.get_column_value(row, username_column_name)
            if (username == None):
                username = email
            if (username != None):
                user['username'] = username
                
            identity_type = self.get_column_value(row, identity_type_column_name)
            if (identity_type != None):
                try:
                    user['identitytype'] = aedash.sync.identity_type.parse_identity_type(identity_type) 
                except aedash.sync.error.AssertionException as e:
                    logger.error('%s for user: %s', e.message, username)
                    e.set_reported()
                    raise e

            domain = self.get_column_value(row, domain_column_name)
            if (domain != None):
                user['domain'] = domain

        return users
    
    def get_column_value(self, row, column_name):
        '''
        :type row: dict
        :type column_name: str
        '''
        value = row.get(column_name)
        if (value == ''):
            value = None
        return value
    
