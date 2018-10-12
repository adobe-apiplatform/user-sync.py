# Copyright (c) 2016-2017 Adobe Inc.  All rights reserved.
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

import csv

from user_sync.connector import helper
from user_sync.connector.umapi import ActionManager
from user_sync.connector.umapi import Commands
import user_sync.identity_type

def write_to_separated_value_file(field_names, delimiter, items, output_file_path):
    with open(output_file_path, 'w', 1) as output_file:
        writer = csv.DictWriter(output_file, fieldnames = field_names, delimiter = delimiter)
        writer.writeheader()
        for item in items:
            writer.writerow(item)

def assert_equal_field_values(unit_test, item1, item2, field_names):
    for field_name in field_names:
        unit_test.assertEqual(item1[field_name], item2[field_name])

next_user_id = 1
def create_test_user(groups):
    global next_user_id
    firstName = 'User_%d' % next_user_id
    next_user_id += 1    
    user = {
        'identity_type': 'enterpriseID',
        'firstname': firstName,
        'lastname': 'Test',
        'email': '%s_email@example.com' % firstName,
        'country': 'CA' if (next_user_id % 2 == 0) else 'US',
        'groups': groups
    }
    return user

def create_test_user_uid():
    global next_user_id
    firstName = 'User_%d' % next_user_id
    uid = '0000%s' % next_user_id
    next_user_id += 1
    user = {
        'uid': uid,
        'identity_type': 'enterpriseID',
        'firstname': firstName,
        'lastname': 'Test',
        'email': '%s_email@example.com' % firstName,
        'country': 'CA' if (next_user_id % 2 == 0) else 'US',
        'groups': []
    }
    return user


def assert_equal_users(unit_test, expected_users, actual_users):
    actual_users_by_email = dict((user['email'], user) for user in actual_users)
    unit_test.assertEqual(len(expected_users), len(actual_users_by_email))

    for expected_user in expected_users:
        actual_user = actual_users_by_email.get(expected_user['email'])
        unit_test.assertIsNotNone(expected_user)            
        assert_equal_field_values(unit_test, expected_user, actual_user,
                                  ['firstname', 'lastname', 'email', 'country'])
        unit_test.assertSetEqual(set(expected_user['groups']), set(actual_user['groups']))

def assert_equal_umapi_commands(unit_test, expected_commands, actual_commands):
    unit_test.assertEqual(expected_commands.__dict__, actual_commands.__dict__)

def assert_equal_umapi_commands_list(unit_test, expected_commands_list, actual_commands_list):
    unit_test.assertEqual(len(expected_commands_list), len(actual_commands_list))    
    expected_list = sorted(expected_commands_list, key=lambda commands: commands.username)
    actual_list = sorted(actual_commands_list, key=lambda commands: commands.username)    
    for i in range(0, len(expected_list) - 1):
        expected_commands = expected_list[i]
        actual_commands = actual_list[i]
        assert_equal_umapi_commands(unit_test, expected_commands, actual_commands)
        
def create_umapi_commands(user, identity_type = user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE):
    commands = Commands(identity_type=identity_type,
                        email=user['email'], username=user['username'], domain=user['domain'])
    return commands

def create_logger():
    return helper.create_logger({"logger_name" : "connector.umapi"})

def create_action_manager():
    return ActionManager(None, "test org id", create_logger())

class MockDictConfig():
    def get_string(self,test1,test2):
        return 'test'

    def get_int(self,test1):
        return 1

    def iter_dict_configs(self):
        return iter([])

    def get_list(self,test1,test2):
        return []
