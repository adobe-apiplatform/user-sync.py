import unittest

import mock

import user_sync
import tests.helper

from user_sync.connector.dashboard import Commands

class ActionManagerTest(unittest.TestCase):
    def setUp(self):
        # setup for each test
        self.action_man = tests.helper.create_action_manager()
        user_sync.connector.dashboard.ActionManager.next_request_id = 1

        self.mock_commands1 = Commands(username="testUserName1", domain="test.com")
        self.mock_commands1.add_groups(['group1']);
        
        self.mock_commands2 = Commands(username="testUserName2", domain="test.com")

    def test_start_with_1_request(self):
        self.assertEquals(self.action_man.next_request_id, 1, "We start with 1 request")

    def test_create_two_actions(self):
        self.action_man.create_action(self.mock_commands1)
        self.assertEquals(self.action_man.next_request_id, 2,
                          "We have created an action and the count has been increased")

        self.action_man.create_action(self.mock_commands2)
        self.assertEquals(self.action_man.next_request_id, 3, "We have created another action and the count increased")

    def test_has_no_work(self):
        self.assertEquals(self.action_man.has_work(), False, "No actions added, therefore hasWork is false")

    @mock.patch('user_sync.connector.dashboard.ActionManager._execute_action')
    def test_has_work(self, mock_execute):
        self.action_man.add_action(self.action_man.create_action(self.mock_commands1), None)
        self.assertEquals(self.action_man.has_work(), True, "An action was added, therefore hasWork is true")
        self.assertEquals(mock_execute.call_count, 1)

