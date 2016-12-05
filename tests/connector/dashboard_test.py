import unittest
from umapi import UMAPI, Action

import mock

import time

from umapi import UMAPI
from umapi.error import UMAPIRetryError
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


class APICallTests(unittest.TestCase):
    def test_retry(self):
        # Ensure that if the method fails, we retry 4 times
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
