import helper
import csv

def connector_metadata():
    metadata = {
        'name': CSVConnector.name,
        'required_options': ['filename']
    }
    return metadata

def connector_initialize(options):
    '''
    :type options: dict
    '''
    state = CSVConnector(options)
    return state


def connector_get_users_with_groups(state, groups):
    '''
    :type state: CSVConnector
    :type groups: list(str)
    :rtype list(dict)
    '''
    return state.get_users_with_groups(groups)

def connector_is_existing_username(state, username):
    '''
    :type state: CSVConnector
    :type username: str
    :rtype bool
    '''
    return state.is_existing_username(username)

class CSVConnector(helper.ConnectorImplementation):
    name = 'csv'
    
    def __init__(self, caller_options):
        options = {
            'delimiter': ',',
            'first_name_column_name': 'firstname',
            'last_name_column_name': 'lastname',
            'email_column_name': 'email',
            'country_column_name': 'country',
            'groups_column_name': 'groups',
            'logger_name': 'connector.' + CSVConnector.name
        }
        options.update(caller_options)

        super(CSVConnector, self).__init__(options)
        logger = self.get_logger()
        
        filename = options['filename']
        
        logger.info('Reading from: %s', filename)
        with open(filename, 'r', 1) as input_file:
            reader = csv.DictReader(input_file, delimiter = options['delimiter'])
            self.users = users = self.read_users(reader)    
        
        logger.info('Number of users loaded: %d', len(users))

    def get_users_with_groups(self, groups):
        '''
        :type groups: list(str)
        :rtype list(dict)
        '''
        
        result = []    
        group_set = set(groups)
        for user in self.users.itervalues():
            if (not(group_set.isdisjoint(user['groups']))):
                result.append(user)
        return result

    def is_existing_username(self, username):
        '''
        :type username: str
        :rtype bool
        '''
        return username in self.users

    def read_users(self, reader):
        '''
        :type reader: csv.DictReader
        :rtype dict
        '''
        users = {}
        
        options = self.get_options()
        logger = self.get_logger()
        
        email_column_name = options['email_column_name']
        first_name_column_name = options['first_name_column_name']
        last_name_column_name = options['last_name_column_name']
        country_column_name = options['country_column_name']
        groups_column_name = options['groups_column_name']
    
        line_read = 0
        for row in reader:
            line_read += 1
            email = self.get_column_value(row, email_column_name)
            if (email == None):
                logger.warning('No email found at row: %d', line_read)
                continue;
            
            user = users.get(email)
            if (user == None):
                user = helper.create_blank_user()
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
    
if True and __name__ == '__main__':
    import sys
    import datetime

    start1 = datetime.datetime.now()    
    options = {
        'filename': "test.csv",
    }
    connector = helper.Connector(sys.modules[__name__], options)
    users = connector.get_users_with_groups(["a", "g"])
    start2 = datetime.datetime.now()
    start3 = start2 - start1
    print("3: " + str(start3));
    