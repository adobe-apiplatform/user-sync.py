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

import csv
import os
import re
import yaml

from user_sync.connector import helper
from user_sync.connector.dashboard import ActionManager
from user_sync.connector.dashboard import Commands
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

def assert_eq(unit_test, result, expected, error_message):
    '''
    compares the result against the expected value, and outputs an error
    message if they don't match. Also outputs the expected and result
    values.
    '''
    unit_test.assertEqual(expected, result, error_message + '\nexpected: %s, got: %s' % (expected, result))

def assert_dict_eq(unit_test, res, exp, err_msg):
    '''
    compares the result dict against the expected dict, and recursively
    asserts that their content matches. The error message is given if an
    error was encountered, and the expected and actual results are given
    as well.
    '''
    def assert_sub_value_eq(res, exp):
        '''
        used to recursively assert that values are equal. If it's a dict or
        list, drill down into then to assert that their entries are equivalent,
        otherwise just compare the values directly.
        '''
        if isinstance(res, dict):
            assert_sub_dict_eq(res, exp)
        elif isinstance(res, list):
            assert_sub_list_eq(res, exp)
        else:
            unit_test.assertEqual(res, exp)
    
    def assert_sub_list_eq(res, exp):
        '''
        compares the result list against the expected list recursively, and
        raises an assertion error if ti's values or sub-values don't match
        '''
        unit_test.assertIsInstance(exp, list, 'expected is not dict')
        unit_test.assertIsInstance(res, list, 'result is not list')
        
        unit_test.assertEqual(len(exp), len(res), 'expected and result lists don\'t have the same number of entries')
        
        for exp_item, res_item in zip(exp, res):
            assert_sub_value_eq(exp_item, res_item)

    def assert_sub_dict_eq(res, exp):
        '''
        compares the result dict against the expected dict recursively, and
        raises an assertion error if it's values or sub-values don't match.
        '''
        unit_test.assertIsInstance(exp, dict, 'expected is not dict')
        unit_test.assertIsInstance(res, dict, 'result is not dict')
        
        unit_test.assertEqual(len(res.keys()), len(exp.keys()), 'expected and result dicts don\'t have the same number of keys')

        for key in exp.keys():
            assert_sub_value_eq(res[key], exp[key])
        
    try:
        assert_sub_dict_eq(res, exp)
    except AssertionError as e:
        raise AssertionError('%s\n%s' % (err_msg, e.message))
    
def assert_config(unit_test, res_dict, exp_file):
    '''
    tests the result dictionary against a expected dictionary. The expected
    dictionary is loaded from a file, and replaces instances of double curly
    braces containing a path with an native absolute path.
    '''
    with open(exp_file, 'r', 1) as input_file:
        exp_str = input_file.read()
    
    def native_path_callback(match):
        return os.path.abspath(match.group(1))
    
    exp_str = re.sub(r'\{\{(.*)\}\}', native_path_callback, exp_str)
    exp_dict = yaml.load(exp_str)
    
    assert_dict_eq(unit_test, res_dict, exp_dict, 'result does not match expected result')

def assert_configs(unit_test, res_list):
    '''
    tests the list of dictionary results against the corresponding expectations
    '''
    for res_map in res_list:
        assert_config(unit_test, res_map['result'], res_map['expected'])

def assert_equal_users(unit_test, expected_users, actual_users):
    actual_users_by_email = dict((user['email'], user) for user in actual_users)
    unit_test.assertEqual(len(expected_users), len(actual_users_by_email))

    for expected_user in expected_users:
        actual_user = actual_users_by_email.get(expected_user['email'])
        unit_test.assertIsNotNone(expected_user)            
        assert_equal_field_values(unit_test, expected_user, actual_user, ['firstname', 'lastname', 'email', 'country'])
        unit_test.assertSetEqual(set(expected_user['groups']), set(actual_user['groups']))

def assert_equal_dashboard_commands(unit_test, expected_commands, actual_commands):
    unit_test.assertEqual(expected_commands.__dict__, actual_commands.__dict__)

def assert_equal_dashboard_commands_list(unit_test, expected_commands_list, actual_commands_list):
    unit_test.assertEqual(len(expected_commands_list), len(actual_commands_list))    
    expected_list = sorted(expected_commands_list, key=lambda commands: commands.username)
    actual_list = sorted(actual_commands_list, key=lambda commands: commands.username)    
    for i in range(0, len(expected_list) - 1):
        expected_commands = expected_list[i]
        actual_commands = actual_list[i]
        assert_equal_dashboard_commands(unit_test, expected_commands, actual_commands)
        
def create_dashboard_commands(user, identity_type = user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE):
    commands = Commands(identity_type=identity_type, email=user['email'], username=user['username'], domain=user['domain'])
    return commands

def create_logger():
    return helper.create_logger({"logger_name" : "connector.dashboard"})

def create_action_manager():
    return ActionManager(None, "test org id", create_logger())

class MockGetString():
    def get_string(self,test1,test2):
        return 'test'

    def get_int(self,test1):
        return 1

    def iter_dict_configs(self):
        return iter([])

    def get_list(self,test1,test2):
        return []
