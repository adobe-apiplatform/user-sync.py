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


import unittest
import mock
import logging
import okta
import json

from user_sync.error import AssertionException
from user_sync.connector.directory_okta import OktaDirectoryConnector, \
    OKTAValueFormatter, connector_load_users_and_groups


class TestOKTAValueFormatter(unittest.TestCase):
    def test_get_extended_attribute_dict(self):
        print 'Used to compare input and expected output data after OKTA formatting def Call'
        attributes = ['firstName', 'lastName', 'login', 'email', 'countryCode']
        expectedresult = str("{'countryCode': <type 'str'>, 'lastName': <type 'str'>, 'login': <type 'str'>, 'email': <type 'str'>, 'firstName': <type 'str'>}")

        self.assertEqual(expectedresult, str(OKTAValueFormatter.get_extended_attribute_dict(attributes)), 'Getting expected Output')


class TestOktaErrors(unittest.TestCase):
    def setUp(self):
        class MockResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self.text = json.dumps(data)

        self.mock_response = MockResponse

        self.orig_directory_init = OktaDirectoryConnector.__init__

        OktaDirectoryConnector.__init__ = mock.Mock(return_value=None)
        directory = OktaDirectoryConnector({})
        directory.options = {'source_filters': {}, 'all_users_filter': None, 'group_filter_format': '{group}'}
        directory.logger = mock.create_autospec(logging.Logger)
        directory.groups_client = okta.UserGroupsClient('example.com', 'xyz')

        self.directory = directory

    def tearDown(self):
        OktaDirectoryConnector.__init__ = self.orig_directory_init

    @mock.patch('okta.framework.ApiClient.requests')
    def test_error_get_group(self, mock_requests):
        # Mock an error response and make sure that the Okta connector catches the exception
        # This will happen in the get_groups() method, which is the first time the UserGroupsClient is called

        mock_requests.get.return_value = self.mock_response(404, {
          "errorCode": "E0000007",
          "errorSummary": "Not found: Resource not found: users (UserGroup)",
          "errorLink": "E0000007",
          "errorId": "oaepKQbQ-_FQ7y5YxDQWFw5Vg",
          "errorCauses": []
        })

        self.assertRaises(AssertionException,
                          connector_load_users_and_groups, self.directory, ['group1', 'group2'], [])


class TestOktaGroupFilter(unittest.TestCase):
    def setUp(self):
        class MockResponse:
            def __init__(self, status_code, data):
                self.status_code = status_code
                self.text = json.dumps(data)

        self.mock_response = MockResponse

        self.orig_directory_init = OktaDirectoryConnector.__init__

        OktaDirectoryConnector.__init__ = mock.Mock(return_value=None)
        directory = OktaDirectoryConnector({})

        directory.logger = mock.create_autospec(logging.Logger)
        directory.groups_client = okta.UserGroupsClient('example.com', 'xyz')

        self.directory = directory

    def tearDown(self):
        OktaDirectoryConnector.__init__ = self.orig_directory_init

    @mock.patch('okta.framework.ApiClient.requests')
    def test_success_group_filter(self, mock_requests):
        # This test success group filter with valid Group
        # This should return Okta GroupsClient Object and Contained property Profile.

        mock_requests.get.return_value = self.mock_response(200, [
            {"id": "00g9sq2jcqpk3LwCV0h7",
             "objectClass": ["okta:user_group"], "type": "OKTA_GROUP",
             "profile": {"name": "Group 1", "description": "null"}}])
        directory = self.directory
        directory.options = {'source_filters': {}, 'all_users_filter': None, 'group_filter_format': '{group}'}
        result = directory.find_group("Group 1")
        self.assertEqual(result.profile.name, "Group 1")

    @mock.patch('okta.framework.ApiClient.requests')
    def test_bad_group_filter_1(self, mock_requests):
        # Test scenario where Group Filter is bad
        # This will not return any group because it can't be find.

        mock_requests.get.return_value = self.mock_response(200, [])
        directory = self.directory
        directory.options = {'source_filters': {}, 'all_users_filter': None,
                             'group_filter_format': '(BADFILTER){group}'}
        result = directory.find_group("Group 1")
        self.assertEqual(result, None)

    def test_bad_group_filter_2(self):
        # Test another scenario of bad group filter - {groupA} instead of {group}
        # This should throw an exception

        directory = self.directory
        directory.options = {'source_filters': {}, 'all_users_filter': None,
                             'group_filter_format': '{groupA}'}
        self.assertRaises(AssertionException, directory.find_group, "Group 1")

