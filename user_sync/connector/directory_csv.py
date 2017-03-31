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

import six

import user_sync.config
import user_sync.connector.helper
import user_sync.error
import user_sync.helper
import user_sync.identity_type

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

def connector_load_users_and_groups(state, groups, extended_attributes):
    '''
    :type state: CSVDirectoryConnector
    :type groups: list(str)
    :type extended_attributes: list(str)
    :rtype (bool, iterable(dict))
    '''

    # CSV supports arbitrary aka "extended" attrs by default, so the value of extended_attributes has no impact on this particular connector

    return state.load_users_and_groups(groups, extended_attributes)

class CSVDirectoryConnector(object):
    name = 'csv'
    
    def __init__(self, caller_options):
        caller_config = user_sync.config.DictConfig('"%s options"' % CSVDirectoryConnector.name, caller_options)
        builder = user_sync.config.OptionsBuilder(caller_config)
        builder.set_string_value('delimiter', None)
        builder.set_string_value('first_name_column_name', 'firstname')
        builder.set_string_value('last_name_column_name', 'lastname')
        builder.set_string_value('email_column_name', 'email')
        builder.set_string_value('country_column_name', 'country')
        builder.set_string_value('groups_column_name', 'groups')
        builder.set_string_value('username_column_name', 'username')
        builder.set_string_value('domain_column_name', 'domain')
        builder.set_string_value('identity_type_column_name', 'type')
        builder.set_string_value('user_identity_type', None)
        builder.set_string_value('logger_name', CSVDirectoryConnector.name)
        builder.require_string_value('file_path')
        options = builder.get_options()

        # identity type for new users if not specified in column
        self.user_identity_type = user_sync.identity_type.parse_identity_type(options['user_identity_type'])

        self.options = options
        self.logger = logger = user_sync.connector.helper.create_logger(options)        
        caller_config.report_unused_values(logger)

        logger.debug('Initialized with options: %s', options)            

    def load_users_and_groups(self, groups, extended_attributes):
        '''
        :type groups: list(str)
        :rtype (bool, iterable(dict))
        '''        
        options = self.options
        file_path = options['file_path']
        self.logger.debug('Reading from: %s', file_path)
        self.users = users = self.read_users(file_path, extended_attributes)
        self.logger.debug('Number of users loaded: %d', len(users))
        return six.itervalues(users)

    def read_users(self, file_path, extended_attributes):
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

        # extended attributes appear after the standard ones (if no header row)
        recognized_column_names += extended_attributes
        
        line_read = 0
        rows = user_sync.helper.iter_csv_rows(file_path, 
                                                delimiter = options['delimiter'], 
                                                recognized_column_names = recognized_column_names, 
                                                logger = logger)
        for row in rows:
            line_read += 1
            email = self.get_column_value(row, email_column_name)
            if email is None or email.find('@') < 0:
                logger.warning('Missing or invalid email at row: %d; skipping', line_read)
                continue;
            
            user = users.get(email)
            if user is None:
                user = user_sync.connector.helper.create_blank_user()
                user['email'] = email
                users[email] = user
            
            first_name = self.get_column_value(row, first_name_column_name)
            if first_name is not None:
                user['firstname'] = first_name
            else:
                logger.debug('No value firstname for: %s', email)
                
            last_name = self.get_column_value(row, last_name_column_name)
            if last_name is not None:    
                user['lastname'] = last_name
            else:
                logger.debug('No value lastname for: %s', email)
    
            country = self.get_column_value(row, country_column_name)
            if country is not None:    
                user['country'] = country
                
            groups = self.get_column_value(row, groups_column_name)
            if groups is not None:
                user['groups'].extend(groups.split(','))
                
            username = self.get_column_value(row, username_column_name)
            if username is None:
                username = email
            user['username'] = username
                
            identity_type = self.get_column_value(row, identity_type_column_name)
            if identity_type:
                try:
                    user['identity_type'] = user_sync.identity_type.parse_identity_type(identity_type)
                except user_sync.error.AssertionException as e:
                    logger.error('%s for user: %s', e.message, username)
                    e.set_reported()
                    raise e
            else:
                identity_type = self.user_identity_type

            domain = self.get_column_value(row, domain_column_name)
            if domain:
                user['domain'] = domain
            elif username != email:
                user['domain'] = email[email.find('@')+1:]

            sa = {}
            for col in recognized_column_names:
                sa[col] = self.get_column_value(row, col)
            user['source_attributes'] = sa

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
    
