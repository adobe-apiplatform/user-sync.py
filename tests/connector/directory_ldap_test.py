import mock.mock
import re
import unittest

import user_sync.connector.directory
import user_sync.connector.directory_ldap
import tests.helper

class LDAPDirectoryTest(unittest.TestCase):

    def test_normal(self):
        user1 = tests.helper.create_test_user([])
        user2 = tests.helper.create_test_user([])
        user3 = tests.helper.create_test_user([])
        all_users = [user1, user2, user3]

        ldap_options = {
            'host': 'test_host', 
            'username': 'test_user',
            'password': 'xxx',
            'base_dn': 'test_base_dn'
        }

        import ldap.ldapobject        
        connection = mock.mock.create_autospec(ldap.ldapobject.LDAPObject)
        
        def mock_initialize(*args, **kwargs):
            self.assertEqual(ldap_options['host'], args[0])
            return connection
        
        def mock_simple_bind_s(*args, **kwargs):
            self.assertEqual(ldap_options['username'], args[0])
            self.assertEqual(ldap_options['password'], args[1])
        
        def mock_search_s(*args, **kwargs):
            search_result = re.search('cn=(.*?)\)', kwargs['filterstr'])            
            group_name = search_result.group(1)
            return [(group_name, {})]

        def mock_search_ext(*args, **kwargs):
            return kwargs['filterstr']
    
        def mock_result3(*args, **kwargs):
            rtype = ldap.RES_SEARCH_RESULT
            rmsgid = None
            serverctrls = []
            rdata = [(user['firstname'], {
                'givenName': [user['firstname']],
                'sn': [user['lastname']],
                'c': [user['country']],
                'mail': [user['email']],
            }) for user in all_users]
            return rtype, rdata, rmsgid, serverctrls

        ldap.initialize = mock_initialize
        connection.simple_bind_s = mock_simple_bind_s
        connection.search_s = mock_search_s
        connection.search_ext = mock_search_ext
        connection.result3 = mock_result3

        directory_connector = user_sync.connector.directory.DirectoryConnector(user_sync.connector.directory_ldap)
        directory_connector.initialize(ldap_options)
 
        actual_users = directory_connector.load_users_and_groups(None)

        tests.helper.assert_equal_users(self, all_users, actual_users)
