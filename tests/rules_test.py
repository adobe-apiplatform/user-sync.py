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

import mock.mock
import unittest

import user_sync.connector.dashboard
import user_sync.connector.directory
import user_sync.rules
import tests.helper

class RulesTest(unittest.TestCase):
    
    def test_normal(self):
        owning_organization_name = user_sync.rules.OWNING_ORGANIZATION_NAME
        accessor_1_organization_name = "accessor1"
        directory_group_1 = 'acrobat1' 
        directory_group_2 = 'acrobat2' 
        owning_group_11 = 'acrobat11' 
        owning_group_12 = 'acrobat12' 
        owning_group_21 = 'acrobat21' 
        directory_groups = {
            directory_group_1: [user_sync.rules.Group(owning_group_11, owning_organization_name), user_sync.rules.Group('acrobat12', accessor_1_organization_name)],
            directory_group_2: [user_sync.rules.Group(owning_group_21, owning_organization_name)]
        }
        all_users = [tests.helper.create_test_user([directory_group_1]), 
            tests.helper.create_test_user([directory_group_2]),
            tests.helper.create_test_user([])]
        
        for user in all_users:
            user['username'] = user['email']
            user['domain'] = None
            
        owning_users = []
        owning_user_1 = all_users[1].copy()
        owning_user_1['groups'] = [owning_group_11]
        owning_users.append(owning_user_1)
        
        def mock_load_users_and_groups(groups):
            return (True, list(all_users))
        mock_directory_connector = mock.mock.create_autospec(user_sync.connector.directory.DirectoryConnector)
        mock_directory_connector.load_users_and_groups = mock_load_users_and_groups
        
        owning_commands_list = []    
        mock_owning_dashboard_connector = self.create_mock_dashboard_connector(owning_users, owning_commands_list)

        accessor_commands_list = []    
        mock_accessor_dashboard_connector = self.create_mock_dashboard_connector([], accessor_commands_list)
        
        dashboard_connectors = user_sync.rules.DashboardConnectors(mock_owning_dashboard_connector, {
            accessor_1_organization_name: mock_accessor_dashboard_connector
        })
        
        rule_processor = user_sync.rules.RuleProcessor({})
        rule_processor.run(directory_groups, mock_directory_connector, dashboard_connectors)

        rule_options = rule_processor.options

        expected_owning_commands_list = []
        
        user = all_users[1]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_groups(set([owning_group_21]))
        commands.remove_groups(set([owning_group_11]))
        expected_owning_commands_list.append(commands)
        
        user = all_users[0]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_user(self.create_user_attributes_for_commands(user, rule_options['update_user_info']))
        commands.add_groups(set([owning_group_11]))        
        expected_owning_commands_list.append(commands)
        
        user = all_users[2]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_user(self.create_user_attributes_for_commands(user, rule_options['update_user_info']))
        expected_owning_commands_list.append(commands)
                
        expected_accessor_commands_list = []
        user = all_users[0]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_groups(set([owning_group_12]))
        expected_accessor_commands_list.append(commands)

        tests.helper.assert_equal_dashboard_commands_list(self, expected_owning_commands_list, owning_commands_list)
        tests.helper.assert_equal_dashboard_commands_list(self, expected_accessor_commands_list, accessor_commands_list)

    # default country code tests
    
    def _do_country_code_test(self, mock_dashboard_commands, mock_connectors, identity_type, default_country_code, user_country_code, expected_country_code):
        expected_result = {'lastname': 'User1', 'email': 'cceuser1@ensemble.ca', 'firstname': '!Openldap CCE', 'option': 'updateIfAlreadyExists'}
        if (expected_country_code):
            expected_result['country'] = expected_country_code

        options = {'default_country_code': default_country_code, 'new_account_type': identity_type}         
        mock_rules = user_sync.rules.RuleProcessor(options)
        mock_rules.directory_user_by_user_key = {
            'cceuser1@ensemble.ca': {'username': 'cceuser1@ensemble.ca',
                                     'domain': None, 'groups': ['CCE Group 1'],
                                     'firstname': '!Openldap CCE',
                                     'country': user_country_code,
                                     'lastname': 'User1',
                                     'identitytype': None,
                                     'email': 'cceuser1@ensemble.ca',
                                     'uid': '001'}
        }
        mock_rules.add_dashboard_user('cceuser1@ensemble.ca', mock_connectors)
        mock_dashboard_commands.return_value.add_user.assert_called_with(expected_result)

    # federatedId
    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_federatedId_no_country_no_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'federatedID', None, None, None)

    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_federatedId_country_supplied_no_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'federatedID', None, 'UK', 'UK')

    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_federatedId_country_supplied_with_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'federatedID', 'US', 'UK', 'UK')

    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_federatedId_no_country_with_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'federatedID', 'US', None, 'US')

    # enterpriseId
    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_enterpriseID_no_country_no_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'enterpriseID', None, None, 'UD')

    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_enterpriseID_country_supplied_no_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'enterpriseID', None, 'UK', 'UK')

    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_enterpriseID_country_supplied_with_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'enterpriseID', 'US', 'UK', 'UK')

    @mock.patch('user_sync.rules.DashboardConnectors')
    @mock.patch('user_sync.connector.dashboard.Commands')
    def test_default_country_enterpriseID_no_country_with_default(self, mock_dashboard_commands, mock_connectors):
        self._do_country_code_test(mock_dashboard_commands, mock_connectors, 'enterpriseID', 'US', None, 'US')

    @staticmethod
    def create_user_attributes_for_commands(user, update_user_info):
        return {
            'email': user['email'],
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'country': user['country'],
            'option': 'updateIfAlreadyExists' if update_user_info else 'ignoreIfAlreadyExists'
        }
        
    @staticmethod
    def create_mock_dashboard_connector(users_to_return, commands_list_output):
        def mock_send_commands(commands, callback = None):
            if (len(commands) > 0):
                commands_list_output.append(commands)
            if (callback != None):
                callback({
                    "action": None, 
                    "is_success": True, 
                    "errors": None
                })

        action_manager = mock.mock.create_autospec(user_sync.connector.dashboard.ActionManager)
        action_manager.has_work = lambda: False
        mock_connector = mock.mock.create_autospec(user_sync.connector.dashboard)
        mock_connector.iter_users = lambda: list(users_to_return)
        mock_connector.send_commands = mock_send_commands
        mock_connector.get_action_manager = lambda: action_manager
        return mock_connector

