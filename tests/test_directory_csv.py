import string
import tempfile
import unittest

import aedash.sync.connector.directory
import aedash.sync.connector.directory_csv
import tests.helper

class TestDirectoryCSV(unittest.TestCase):

    def test_normal(self):
        _, file_path = tempfile.mkstemp(".csv")
        
        field_names = ['firstname', 'lastname', 'email', 'country', 'groups']
        item1_groups = ['Acrobat1', 'Acrobat2'];
        item1 = {
            'firstname': 'John',
            'lastname': 'Smith',
            'email': 'jsmith@example.com',
            'country': 'CA',
            'groups': string.join(item1_groups, ',')
        }
        tests.helper.write_to_separated_value_file(field_names, ',', [item1], file_path);
        
        directory_connector = aedash.sync.connector.directory.DirectoryConnector(aedash.sync.connector.directory_csv)
        options = {
            'file_path': file_path
        }
        directory_connector.initialize(options)
        all_loaded, users = directory_connector.load_users_and_groups(item1_groups)
                
        self.assertTrue(all_loaded)
        
        users = list(users)
        self.assertEqual(1, len(users))
        
        user = users[0]
        tests.helper.assert_equal_field_values(self, item1, user, ['firstname', 'lastname', 'email', 'country'])
        self.assertEqual(item1_groups, user['groups'])
