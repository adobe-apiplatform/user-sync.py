import mock.mock
import unittest

import aedash.sync.connector.dashboard
import aedash.sync.connector.directory
import aedash.sync.rules
import tests.helper

class RulesTest(unittest.TestCase):
    
    def test_normal(self):
        owning_organization_name = aedash.sync.rules.OWNING_ORGANIZATION_NAME
        trustee_1_organization_name = "trustee1"
        directory_group_1 = 'acrobat1' 
        directory_group_2 = 'acrobat2' 
        owning_group_11 = 'acrobat11' 
        owning_group_12 = 'acrobat12' 
        owning_group_21 = 'acrobat21' 
        directory_groups = {
            directory_group_1: [aedash.sync.rules.Group(owning_group_11, owning_organization_name), aedash.sync.rules.Group('acrobat12', trustee_1_organization_name)],
            directory_group_2: [aedash.sync.rules.Group(owning_group_21, owning_organization_name)]
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
        mock_directory_connector = mock.mock.create_autospec(aedash.sync.connector.directory.DirectoryConnector)
        mock_directory_connector.load_users_and_groups = mock_load_users_and_groups
        
        owning_commands_list = []    
        mock_owning_dashboard_connector = self.create_mock_dashboard_connector(owning_users, owning_commands_list)

        trustee_commands_list = []    
        mock_trustee_dashboard_connector = self.create_mock_dashboard_connector([], trustee_commands_list)
        
        dashboard_connectors = aedash.sync.rules.DashboardConnectors(mock_owning_dashboard_connector, {
            trustee_1_organization_name: mock_trustee_dashboard_connector
        })
        
        rule_processor = aedash.sync.rules.RuleProcessor({})
        rule_processor.run(directory_groups, mock_directory_connector, dashboard_connectors)

        rule_options = rule_processor.options

        expected_owning_commands_list = []
        
        user = all_users[1]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_groups([owning_group_21])
        commands.remove_groups([owning_group_11])
        expected_owning_commands_list.append(commands)
        
        user = all_users[0]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_enterprise_user(self.create_user_attributes_for_commands(user, rule_options['update_user_info']))
        commands.add_groups([owning_group_11])        
        expected_owning_commands_list.append(commands)
        
        user = all_users[2]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_enterprise_user(self.create_user_attributes_for_commands(user, rule_options['update_user_info']))
        expected_owning_commands_list.append(commands)
                
        expected_trustee_commands_list = []
        user = all_users[0]
        commands = tests.helper.create_dashboard_commands(user)
        commands.add_groups([owning_group_12])
        expected_trustee_commands_list.append(commands)

        tests.helper.assert_equal_dashboard_commands_list(self, expected_owning_commands_list, owning_commands_list)
        tests.helper.assert_equal_dashboard_commands_list(self, expected_trustee_commands_list, trustee_commands_list)

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
                callback(None, True, None)

        action_manager = mock.mock.create_autospec(aedash.sync.connector.dashboard.ActionManager)
        action_manager.has_work = lambda: False
        mock_connector = mock.mock.create_autospec(aedash.sync.connector.dashboard)
        mock_connector.iter_users = lambda: list(users_to_return)
        mock_connector.send_commands = mock_send_commands
        mock_connector.get_action_manager = lambda: action_manager
        return mock_connector

