from unittest import mock

import pytest

from sign_client.client import SignClient
from tests.util import MockResponse


@pytest.fixture
def example_client():
    return SignClient(host='api.echosign.com',
                      integration_key='3AAABLZtkPdD5io',
                      admin_email='user@example.com'
                      )


def test_base_uri(example_client):
    with mock.patch('sign_client.client.requests') as mocked_requests:
        mocked_requests.get.return_value = MockResponse(body={'api_access_point': 'api_test_value/'})
        result = example_client.base_uri()
        assert result == 'api_test_value/api/rest/v5/'


def test_get_users(example_client):
    user_info_list = {"userInfoList": [{"groupId": "OZR8L8ZDql6m5", "email": "user1@example.com",
                                        "fullNameOrEmail": "test user", "userId": "l3WbzoofzjCmEH5gZcX7"
                                        }]}

    user_details = {"email": "user1@example.com", "group": "Default Group", "roles": "ACCOUNT_ADMIN",
                    "userStatus": "ACTIVE"}
    with mock.patch('sign_client.client.requests') as mocked_requests:
        mocked_requests.get.side_effect = [MockResponse(body=user_info_list), MockResponse(body=user_details)]
        example_client.api_url = 'example.com'
        example_client.groups = []
        result = example_client.get_users()
        assert result['user1@example.com']['email'] == 'user1@example.com'
        assert result['user1@example.com']['group'] == 'Default Group'
        assert result['user1@example.com']['roles'] == 'ACCOUNT_ADMIN'
        assert result['user1@example.com']['userStatus'] == 'ACTIVE'


def test_get_groups(example_client):
    with mock.patch('sign_client.client.requests') as mocked_requests:
        mocked_requests.get.return_value = MockResponse(
            body={'groupInfoList': [{
                'groupId': 'OZR8L8ZDql6m5',
                'groupName': 'Default Group'}, {
                'groupId': 'LBQBZLPrDk7Pn',
                'groupName': 'Group 1'}, {
                'groupId': 'tin31laZIb36L',
                'groupName': 'Group 2'}]}
        )
        example_client.api_url = 'example.com'
        result = example_client.get_groups()
        assert result == {'default group': 'OZR8L8ZDql6m5', 'group 1': 'LBQBZLPrDk7Pn', 'group 2': 'tin31laZIb36L'}
