import string
import tempfile
import unittest

import user_sync.connector.directory
import user_sync.connector.directory_csv
import tests.helper

class CSVDirectoryTest(unittest.TestCase):

    def test_normal(self):
        _, file_path = tempfile.mkstemp(".csv")
        
        field_names = ['identity_type', 'firstname', 'lastname', 'email', 'country', 'groups']
        user1 = tests.helper.create_test_user(['Acrobat1', 'Acrobat2'])
        user2 = tests.helper.create_test_user([])
        
        all_users = [user1, user2]
        all_groups = set()
        csv_users = []
        for user in all_users:
            csv_user = user.copy();
            user_groups = user['groups']
            all_groups.update(user_groups)
            csv_user['groups'] = string.join(user_groups, ',')
            csv_users.append(csv_user)
        tests.helper.write_to_separated_value_file(field_names, ',', csv_users, file_path);
        
        directory_connector = user_sync.connector.directory.DirectoryConnector(user_sync.connector.directory_csv)
        options = {
            'file_path': file_path
        }
        directory_connector.initialize(options)
        
        actual_users = directory_connector.load_users_and_groups(all_groups)
                
        tests.helper.assert_equal_users(self, all_users, actual_users)

