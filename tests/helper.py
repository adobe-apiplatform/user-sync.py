import csv

import time
import email.utils

import user_sync
from user_sync.connector import helper
from user_sync.connector.dashboard import ApiDelegate
from user_sync.connector.dashboard import ActionManager
from user_sync.connector.dashboard import Commands


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
        'firstname': firstName,
        'lastname': 'Test',
        'email': '%s_email@example.com' % firstName,
        'country': 'CA' if (next_user_id % 2 == 0) else 'US',
        'groups': groups
    }
    return user


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
        
def create_dashboard_commands(user):
    commands = Commands(user['username'], user['domain'])
    return commands

def create_logger():
    return helper.create_logger({"logger_name" : "connector.dashboard"})

def create_action_manager():
    return ActionManager(ApiDelegate(None, create_logger()), "test org id", create_logger())

def default_country_options(default_country_code, identity_type):
    return {'default_country_code': default_country_code,
            'new_account_type': identity_type}

def default_country_user(country):
    return {
        'cceuser1@ensemble.ca': {'username': 'cceuser1@ensemble.ca',
                                 'domain': None, 'groups': ['CCE Group 1'],
                                 'firstname': '!Openldap CCE',
                                 'country': country,
                                 'lastname': 'User1',
                                 'identitytype': None,
                                 'email': 'cceuser1@ensemble.ca',
                                 'uid': '001'}}

def default_country_exec(options,country,mock_connectors):
    mock_rules = user_sync.rules.RuleProcessor(options)

    mock_rules.directory_user_by_user_key = default_country_user(country)

    mock_rules.add_dashboard_user('cceuser1@ensemble.ca', mock_connectors)

class MockGetString():
    def get_string(self,test1,test2):
        return 'test'