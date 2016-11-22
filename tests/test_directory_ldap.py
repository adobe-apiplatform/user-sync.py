import mock
import string
import unittest

import aedash.sync.connector.directory
import aedash.sync.connector.directory_ldap
import tests.helper

class TestDirectoryLDAP(unittest.TestCase):

    def test_normal(self):
        item1_dn = "User1"
        item1_groups = ['Acrobat1', 'Acrobat2'];
        item1 = {
            'firstname': 'John',
            'lastname': 'Smith',
            'email': 'jsmith@example.com',
            'country': 'CA',
            'groups': string.join(item1_groups, ',')
        }

        import ldap.ldapobject        
        connection = mock.create_autospec(ldap.ldapobject.LDAPObject)
        ldap.initialize = mock.MagicMock(return_value = connection)
        
        def mock_search_s(*args, **kwargs):
            return [(kwargs['filterstr'], {
                'member': [item1_dn]
            })]

        def mock_result(*args, **kwargs):
            rtype = ldap.RES_SEARCH_RESULT
            rdata = [(item1_dn, {
                'member': [item1_dn]
            })]
            return rtype, rdata

        def mock_search(*args, **kwargs):
            return kwargs['filterstr']
    
        def mock_search_ext(*args, **kwargs):
            return kwargs['filterstr']
    
        def mock_result3(*args, **kwargs):
            rtype = ldap.RES_SEARCH_RESULT
            rmsgid = None
            serverctrls = []
            rdata = [(item1_dn, {
                'givenName': [item1['firstname']],
                'sn': [item1['lastname']],
                'c': [item1['country']],
                'mail': [item1['email']],
            })]
            return rtype, rdata, rmsgid, serverctrls

        connection.search_s = mock_search_s
        connection.search_ext = mock_search_ext
        connection.result3 = mock_result3
        connection.search = mock_search
        connection.result = mock_result

        directory_connector = aedash.sync.connector.directory.DirectoryConnector(aedash.sync.connector.directory_ldap)
        options = {
            'host': 'test_host', 
            'username': 'test_user',
            'password': 'xxx',
            'base_dn': 'test_base_dn'
        }
        directory_connector.initialize(options)

        all_loaded, users = directory_connector.load_users_and_groups(item1_groups)

        self.assertTrue(all_loaded)

        users = list(users)
        self.assertEqual(1, len(users))

        user = users[0]
        tests.helper.assert_equal_field_values(self, item1, user, ['firstname', 'lastname', 'email', 'country'])
        self.assertEqual(item1_groups, user['groups'])
