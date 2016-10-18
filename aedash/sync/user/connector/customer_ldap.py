from collections import deque 
import helper
import ldap
import string

def connector_metadata():
    metadata = {
        'name': LDAPCustomerConnector.name,
        'required_options': ['host', 'username', 'password', 'base_dn']
    }
    return metadata

def connector_initialize(options):
    '''
    :type options: dict
    '''
    connector = LDAPCustomerConnector(options)
    return connector

def connector_get_users_with_groups(state, groups):
    '''
    :type state: LDAPCustomerConnector
    :type groups: list(str)
    :rtype list(dict)
    '''
    return state.get_users_with_groups(groups)

def connector_is_existing_username(state, username):
    return True

class LDAPCustomerConnector(object):
    name = 'ldap'
    
    def __init__(self, caller_options):
        options = {
            'group_filter_format': '(&(|(objectCategory=group)(objectClass=groupOfNames))(cn={group}))',
            'require_tls_cert': False,
            'user_email_format': '{mail}',
            'user_username_format': None,
            'user_domain_format': None,
            'user_identity_type': None,
            'logger_name': 'connector.' + LDAPCustomerConnector.name
        }
        options.update(caller_options)
    
        self.user_email_generator = LDAPValueGenerator(options['user_email_format'])
        self.user_username_generator = LDAPValueGenerator(options['user_username_format'])
        self.user_domain_generator = LDAPValueGenerator(options['user_domain_format'])
        
        self.options = options
        self.logger = logger = helper.create_logger(options)
        
        require_tls_cert = options['require_tls_cert']
        host = options['host']
        username = options['username']
        password = options['password']

        logger.info('Connecting to: %s using username: %s', host, username)            
        if not require_tls_cert:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        connection = ldap.initialize(host)
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        connection.simple_bind_s(username, password)
        self.connection = connection
        logger.info('Connected')
        
    def get_users_with_groups(self, groups):
        '''
        :type groups: list(str)
        :rtype list(dict)
        '''
        
        logger = self.logger
    
        users = {}
        user_attribute_names = ["givenName", "sn", "c"]    
        user_attribute_names.extend(self.user_email_generator.get_attribute_names())
        user_attribute_names.extend(self.user_username_generator.get_attribute_names())
        user_attribute_names.extend(self.user_domain_generator.get_attribute_names())
    
        maximum_requests_to_buffer = 500
        requests = deque()
        
        connection = self.connection
    
        for group in groups:
            group_members = self.get_ldap_group_members(group)
            if group_members != None:
                for group_member in group_members:
                    new_user = False
                    if group_member in users:
                        user = users[group_member];
                    else:
                        user = helper.create_blank_user()
                        users[group_member] = user
                        new_user = True
                    user['groups'].append(group)
                    
                    if new_user:
                        msgid = connection.search(group_member, ldap.SCOPE_BASE, attrlist=user_attribute_names)
                        requests.append((msgid, group_member, user))
                        if (maximum_requests_to_buffer > 0):
                            maximum_requests_to_buffer -= 1
                        elif (len(requests) > 0):
                            self.process_one_user_request(requests)
        
        while(len(requests) > 0):
            self.process_one_user_request(requests)
            
        valid_users = []
        for dn, user in users.iteritems():
            if user['email'] == None:
                logger.warning('Skipped user with no email for dn: %s', dn)
                continue
            valid_users.append(user)                    
        return valid_users

    def find_ldap_group(self, group, attribute_list=None):
        '''
        :type group: str
        :type attribute_list: list(str)
        :rtype (str, dict)
        '''
    
        connection = self.connection
        options = self.options
        base_dn = options['base_dn']
        group_filter_format = options['group_filter_format']
        
        res = connection.search_s(
            base_dn,
            ldap.SCOPE_SUBTREE,
            filterstr=group_filter_format.format(group=group),
            attrlist=attribute_list
        )
        
        group_tuple = None;
        for current_tuple in res:
            if (current_tuple[0] != None):
                if (group_tuple != None):
                    raise Exception("Multiple LDAP groups found for: %s" % group)
                group_tuple = current_tuple
        
        return group_tuple

    def get_attribute_values(self, dn, attribute_name, attributes=None):
        '''
        :type group_dn: str
        :type attribute_name: str
        :type group_attributes: dict(str, list)
        :rtype iterator
        '''
        
        connection = self.connection
    
        msgid = None    
        if (attributes == None):
            msgid = connection.search(dn, ldap.SCOPE_BASE, attrlist=[attribute_name])
    
        while (True):
            if (msgid != None):
                result_type, result_response = connection.result(msgid)
                msgid = None
                if ((result_type == ldap.RES_SEARCH_RESULT or result_type == ldap.RES_SEARCH_ENTRY) and len(result_response) > 0):
                    current_tuple = result_response[0];
                    if (current_tuple[0] != None):
                        attributes = current_tuple[1]
            
            if (attributes == None):
                break;
                                        
            for current_attribute_name, current_attribute_values in attributes.iteritems():
                current_attribute_name_parts = current_attribute_name.split(';')
                if (current_attribute_name_parts[0] == attribute_name):
                    if (len(current_attribute_name_parts) > 1):
                        upper_bound = self.get_range_upper_bound(current_attribute_name_parts[1])
                        if (upper_bound != None and upper_bound != '*'):
                            next_attribute_name = "%s;range=%s-*" % (attribute_name, str(int(upper_bound) + 1));                        
                            msgid = connection.search(dn, ldap.SCOPE_BASE, attrlist=[next_attribute_name])
                    for current_attribute_value in current_attribute_values:
                        try:
                            yield current_attribute_value;
                        except GeneratorExit:
                            if (msgid != None):
                                connection.abandon(msgid)
                                msgid = None
                            raise
            attributes = None                 
            
    def get_range_upper_bound(self, range_statement):
        result = None
        if (range_statement != None):
            statement_parts = range_statement.split('=')
            if (statement_parts[0] == 'range' and len(statement_parts) > 1):
                range_parts = statement_parts[1].split('-');
                if (len(range_parts) > 1):
                    result = range_parts[1] 
        return result

    def get_ldap_group_members(self, group):
        '''
        :type group: str
        :rtype iterator
        '''
    
        logger = self.logger
    
        result = None
        group_tuple = self.find_ldap_group(group)
        if (group_tuple == None):
            logger.warning("No group found for: %s", group)
        else:
            group_dn, group_attributes = group_tuple;
            result = self.get_attribute_values(group_dn, 'member', group_attributes)
        return result
        
    def process_one_user_request(self, requests):
        '''
        :type requests: collections.deque
        '''
        msgid, dn, user = requests.popleft()
        try: 
            result_type, result_response = self.connection.result(msgid)
        except:
            pass
            
        logger = self.logger    
            
        if ((result_type == ldap.RES_SEARCH_RESULT or result_type == ldap.RES_SEARCH_ENTRY) and len(result_response) > 0):
            record = result_response[0][1];
            email, last_attribute_name = self.user_email_generator.generate_value(record)
            if (email != None):
                user['email'] = email
            elif (last_attribute_name != None):
                logger.info('No email attribute: %s for dn: %s', last_attribute_name, dn)
                
            username, last_attribute_name = self.user_username_generator.generate_value(record)
            if (username != None):
                user['username'] = username
            elif (last_attribute_name != None):
                logger.info('No username attribute: %s for dn: %s', last_attribute_name, dn)    
                    
            domain, last_attribute_name = self.user_domain_generator.generate_value(record)
            if (domain != None):
                user['domain'] = domain
            elif (last_attribute_name != None):
                logger.info('No domain attribute: %s for dn: %s', last_attribute_name, dn)    
                                                
            given_name_value = LDAPValueGenerator.get_attribute_value(record, 'givenName')
            if (given_name_value != None):   
                user['firstname'] = given_name_value
            sn_value = LDAPValueGenerator.get_attribute_value(record, 'sn')
            if sn_value != None:
                user['lastname'] = sn_value
            c_value = LDAPValueGenerator.get_attribute_value(record, 'c')
            if c_value != None:
                user['country'] = c_value
        else:
            logger.info('No user match for dn: %s', dn)
    
class LDAPValueGenerator(object):
    def __init__(self, string_format):
        '''
        :type string_format: str
        '''        
        if (string_format == None): 
            attribute_names = []
        else:
            formatter = string.Formatter()
            attribute_names = [item[1] for item in formatter.parse(string_format) if item[1]]
            
        self.string_format = string_format        
        self.attribute_names = attribute_names
        
    def get_attribute_names(self):
        '''
        :rtype list(str)
        '''
        return self.attribute_names
    
    def generate_value(self, record):
        '''
        :type parameter_names: list(str)
        :type record: dict
        :type logger: logging
        :rtype (str, str)
        ''' 
        result = None
        attribute_name = None
        if (self.string_format != None):   
            values = {}
            for attribute_name in self.attribute_names:
                value = self.get_attribute_value(record, attribute_name)
                if (value == None):
                    values = None
                    break
                values[attribute_name] = value
            if (values != None):
                result = self.string_format.format(**values)
        return (result, attribute_name)

    @staticmethod
    def get_attribute_value(attributes, attribute_name):
        '''
        :type attributes: dict
        :type attribute_name: str
        '''    
        if attribute_name in attributes:
            attribute_value = attributes[attribute_name]
            if (len(attribute_value) > 0):
                return attribute_value[0]
        return None

    

if True and __name__ == '__main__':
    import sys
    import datetime
    import customer
    
    start1 = datetime.datetime.now()    
    options = {
        'host': "ldap://dev-ad.ensemble.com",
        'username': "CN=ADFS User,CN=Users,dc=ensemble,dc=com",
        'password': "p@ssw0rd!",
        'base_dn': "dc=ensemble,dc=com",
    }
    options['user_email_format'] = '{sAMAccountName}@ensemble.com'
    options['user_domain_format'] = 'ensemble.com'
    options['user_username_format'] = '{mail}'
    connector = customer.CustomerConnector(sys.modules[__name__], options)
    users = connector.get_users_with_groups(["BulkGroup"])
    start2 = datetime.datetime.now()
    start3 = start2 - start1
    print("3: " + str(start3));
