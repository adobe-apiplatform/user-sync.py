from collections import deque 
import logging
import datetime
import ldap
import string

def connector_metadata():
    metadata = {
        'name': 'ldap',
        'required_options': ['host', 'username', 'password', 'base_dn']
    }
    return metadata

def connector_initialize(options):
    '''
    :type options: dict
    '''
    
    result = {
        'group_filter_format': '(&(|(objectCategory=group)(objectClass=groupOfNames))(cn=%s))',
        'require_tls_cert': False,
        'email_format': '{mail}',
    }
    result.update(options)
    
    formatter = string.Formatter()
    result['email_attribute_names'] = [item[1] for item in formatter.parse(result['email_format']) if item[1]]

    require_tls_cert = result['require_tls_cert']
    host = result['host']
    username = result['username']
    password = result['password']
    
    if not require_tls_cert:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    connection = ldap.initialize(host)
    connection.protocol_version = ldap.VERSION3
    connection.set_option(ldap.OPT_REFERRALS, 0)
    connection.simple_bind_s(username, password)
    result['connection'] = connection;    
    return result

def connector_get_users_with_groups(state, groups):
    '''
    :type state: dict
    :type groups: list(str)
    :rtype list(dict)
    '''

    users = {}
    user_attribute_names = ["givenName", "sn", "c"]    
    user_attribute_names.extend(state['email_attribute_names'])

    maximum_requests_to_buffer = 500
    requests = deque()
    
    connection = get_connection(state)

    for group in groups:
        group_members = get_ldap_group_members(state, group)
        if group_members != None:
            for group_member in group_members:
                new_user = False
                if group_member in users:
                    user = users[group_member];
                else:
                    user = {
                        "firstname": None,
                        "lastname": None,
                        "email": None,
                        "groups": [],
                        "country": "",
                    }
                    users[group_member] = user
                    new_user = True
                user['groups'].append(group)
                
                if new_user:
                    msgid = connection.search(group_member, ldap.SCOPE_BASE, attrlist=user_attribute_names)
                    requests.append((msgid, user))
                    if (maximum_requests_to_buffer > 0):
                        maximum_requests_to_buffer -= 1
                    elif (len(requests) > 0):
                        process_one_user_request(state, requests)
    
    while(len(requests) > 0):
        process_one_user_request(state, requests)
        
    valid_users = []
    for dn, user in users.iteritems():
        if user['email'] == None:
            logging.warn('No email for user with dn: %s' % dn)
            continue
        valid_users.append(user)                    
    return valid_users

def connector_is_existing_username(state, username):
    return True

def get_connection(state):
    '''
    :rtype ldap.LDAPObject    
    '''
    return state['connection']

def find_ldap_group(state, group, attribute_list = None):
    '''
    :type state: dict
    :type group: str
    :rtype (str, dict)
    '''

    connection = get_connection(state)
    base_dn = state['base_dn']
    group_filter_format = state['group_filter_format']
    
    res = connection.search_s(
        base_dn,
        ldap.SCOPE_SUBTREE,
        filterstr=group_filter_format % group,
        attrlist=attribute_list
    )
    
    group_tuple = None;
    for current_tuple in res:
        if (current_tuple[0] != None):
            if (group_tuple != None):
                raise Exception("Multiple LDAP groups found for: %s" % group)
            group_tuple = current_tuple
    
    return group_tuple

def get_attribute_values(state, dn, attribute_name, attributes = None):
    '''
    :type state: dict
    :type group_dn: str
    :type attribute_name: str
    :type group_attributes: dict(str, list)
    :rtype iterator
    '''
    
    connection = get_connection(state)

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
                    upper_bound = get_range_upper_bound(current_attribute_name_parts[1])
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
            
def get_range_upper_bound(range_statement):
    result = None
    if (range_statement != None):
        statement_parts = range_statement.split('=')
        if (statement_parts[0] == 'range' and len(statement_parts) > 1):
            range_parts = statement_parts[1].split('-');
            if (len(range_parts) > 1):
                result = range_parts[1] 
    return result

def get_ldap_group_members(state, group):
    '''
    :type state: dict
    :type group: str
    :rtype iterator
    '''

    result = None
    group_tuple = find_ldap_group(state, group)
    if (group_tuple == None):
        logging.warn("No LDAP group found for: %s" % group)
    else:
        group_dn, group_attributes = group_tuple;
        result = get_attribute_values(state, group_dn, 'member', group_attributes)
    return result
    
def process_one_user_request(state, requests):
    '''
    :type state: dict
    :type requests: collections.deque
    '''
    msgid, user = requests.popleft()
    try: 
        result_type, result_response = get_connection(state).result(msgid)
    except:
        pass
        
    if (result_type == ldap.RES_SEARCH_RESULT and len(result_response) > 0):
        _, record = result_response[0];
        email_values = {}
        for email_attribute_name in state['email_attribute_names']:
            value = get_attribute_value(record, email_attribute_name)
            if (value == None):
                email_values = None
                break
            email_values[email_attribute_name] = value
        if (email_values != None):
            user['email'] = state['email_format'].format(**email_values)
        given_name_value =  get_attribute_value(record, 'givenName')
        if (given_name_value != None):   
            user['firstname'] = given_name_value
        sn_value =  get_attribute_value(record, 'sn')
        if sn_value != None:
            user['lastname'] = sn_value
        c_value = get_attribute_value(record, 'c')
        if c_value != None:
            user['country'] = c_value                    

def get_attribute_value(attributes, attribute_name):
    if attribute_name in attributes:
        attribute_value = attributes[attribute_name]
        if (len(attribute_value) > 0):
            return attribute_value[0]
    return None


if False and __name__ == '__main__':
    start1 = datetime.datetime.now()
    
    import helper
    import sys
    
    options = {
        'host': "ldap://dev-ad.ensemble.com",
        'username': "CN=ADFS User,CN=Users,dc=ensemble,dc=com",
        'password': "p@ssw0rd!",
        'base_dn': "dc=ensemble,dc=com",
    }
    options['email_format'] = '{sAMAccountName}@ensemble.com'
    connector = helper.Connector(sys.modules[__name__], options)
    users = connector.get_users_with_groups(["BulkGroup"])
    start2 = datetime.datetime.now()

    start3 = start2 - start1
    print("3: " + str(start3));
