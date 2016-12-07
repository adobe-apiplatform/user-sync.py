import unittest
import logging
from umapi import UMAPI, Action

import mock

import time

from umapi import UMAPI
from umapi.error import UMAPIRetryError, UMAPIError, UMAPIRequestError
import email.utils

import aedash
import tests.helper
from aedash.sync.connector.dashboard import ApiDelegate

class MockRetryResult:
    count = 0

    def __init__(self, wait):
        self.status_code = 501
        retry_on = time.time() + wait
        self.headers = {'Retry-After': email.utils.formatdate(retry_on)}

    def increment(self):
        self.count += 1


class MockSuccessResult:
    def __init__(self):
        self.status_code = 200


class APIDelegateTest(unittest.TestCase):
    def test_retry(self):
        # 2 second delay between retries
        mock_result = MockRetryResult(2)

        def mock_send_retry():
            mock_result.increment()
            raise UMAPIRetryError(mock_result)

        delegate = ApiDelegate({}, tests.helper.create_logger());
        try:
            delegate.make_api_call(mock_send_retry, {});
        except UMAPIRetryError as e:
            pass

        self.assertEquals(mock_result.count, 4, "api call is retried 4 times")

    def test_retry_success(self):
        # Ensure that a successful call is handled correctly
        success_result = MockSuccessResult()

        def mock_api_call():
            return success_result

        delegate = ApiDelegate({}, tests.helper.create_logger());
        result = delegate.make_api_call(mock_api_call, {});

        self.assertEquals(result, success_result, "Successful api call")


class ActionManagerTest(unittest.TestCase):

    def setUp(self):
        # setup for each test
        self.action_man = tests.helper.create_action_manager()
        aedash.sync.connector.dashboard.ActionManager.next_request_id = 1

        self.mock_action1 = Action("testUserName1",{'action':'action'})
        self.mock_action2 = Action("testUserName2",{})

    def test_start_with_1_request(self):
        self.assertEquals(self.action_man.next_request_id, 1,"We start with 1 request")

    def test_add_two_actions(self):
        self.action_man.add_action(self.mock_action1,{})
        self.assertEquals(self.action_man.next_request_id,2,"We have added an action and the count has been increased")

        self.action_man.add_action(self.mock_action2,{})
        self.assertEquals(self.action_man.next_request_id,3,"We have added another action and the count increased")

    def test_has_no_work(self):
        self.assertEquals(self.action_man.has_work(),False,"No actions added, therefore hasWork is false")

    def test_has_work(self):
        self.action_man.add_action(self.mock_action1,{})
        self.assertEquals(self.action_man.has_work(), True, "An action was added, therefore hasWork is true")

    # Boundary Tests for execute method invocation
    @mock.patch('aedash.sync.connector.dashboard.ActionManager.execute')
    def test_add_9_actions(self,mock_execute):
        for x in range(9):
            self.action_man.add_action(self.mock_action1, {})
        self.assertEquals(mock_execute.call_count,0,"execute not called when there are 9 items")

    @mock.patch('aedash.sync.connector.dashboard.ActionManager.execute')
    def test_add_10_actions(self, mock_execute):
        for x in range(10):
            self.action_man.add_action(self.mock_action1, {})
        self.assertEquals(mock_execute.call_count, 1, "execute called when there are 10 items")

    @mock.patch('aedash.sync.connector.dashboard.ActionManager.execute')
    def test_add_11_actions(self, mock_execute):
        for x in range(11):
            self.action_man.add_action(self.mock_action1, {})
        self.assertEquals(mock_execute.call_count, 2, "execute called twice (for items 10 and 11)")

    # Execute tests
    @mock.patch('aedash.sync.connector.dashboard.ApiDelegate.action')
    def test_execute_retry_error(self,mock_delegate):
        mock_delegate.side_effect = UMAPIRetryError(mock.Mock(status_code=2))
        self.action_man.execute()

    @mock.patch('aedash.sync.connector.dashboard.ApiDelegate.action')
    def test_execute_umapi_error(self, mock_delegate):
        mock_delegate.side_effect = UMAPIError(mock.Mock(status_code=2,res_text='expected error'))
        self.action_man.execute()

    @mock.patch('aedash.sync.connector.dashboard.ApiDelegate.action')
    def test_execute_request_error(self, mock_delegate):

        mock_delegate.side_effect = UMAPIRequestError({'result':'success',
                                                       'completed':1,
                                                       'completedInTestMode':1,
                                                       'notCompleted':0,'errors':{}})
        self.action_man.logger.log = mock.Mock()
        self.action_man.execute()
        # request error was logged correctly
        self.action_man.logger.log.assert_called_with(10,'Result %s -- %d completed, %d completedInTestMode, %d failed',
                                                      'success', 1, 1, 0)
