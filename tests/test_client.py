from unittest import mock

import pytest
from mock import MagicMock
from sign_client.client import SignClient


class MockResponse:

    def __init__(self, status=200, body=None, headers=None, text=None):
        self.status_code = status
        self.body = body if body is not None else {}
        self.headers = headers if headers else {}
        self.text = text if text else ""

    def json(self):
        return self.body

@pytest.fixture
def signclient_example():
    return SignClient(host='api.echosignstage.com',
                      integration_key='3AAABLZtkPdD5io2nstgKMyIq7SgmMUc2hpYtvbq2z2is',
                      admin_email='user@example.com'
                      )

def test_base_uri(signclient_example):
    with mock.patch('sign_client.client.requests') as mocked_requests:
        mocked_requests.get.return_value = MockResponse(
            body={
                'api_access_point':'api_test_value/'
            }
        )
        result = signclient_example.base_uri()
        assert result == 'api_test_value/api/rest/v5/'

def test_get_users(signclient_example):
    mock_get = MagicMock()
    with mock.patch('sign_client.client.requests') as mocked_requests:
        mocked_requests.get.return_value = MockResponse(
            body={"userInfoList": [
                    {
                        "groupId": "3AAABLZtkPdAH9sz1KbI8GSydrljH2bmhtjOwhNHD9NnnaEZbGyzjGWiiDkEOGzzF5AVZDCXyBwDiebPyEY-OZR8L8ZDql6m5",
                        "email": "user@example.com",
                        "fullNameOrEmail": "test user",
                        "userId": "3AAABLZtkPdBf9rlRchWj-U8cHaklFlsBIuy2GDZa0x44_dBwCkS8r7vwianWRpwC07JSA6f-UBx6haKX9Nf1z_ZccMMiMwpV"
                    },
                    {
                        "groupId": "3AAABLZtkPdAH9sz1KbI8GSydrljH2bmhtjOwhNHD9NnnaEZbGyzjGWiiDkEOGzzF5AVZDCXyBwDiebPyEY-OZR8L8ZDql6m5",
                        "email": "user@example.com",
                        "fullNameOrEmail": "test user",
                        "company": "Dev Sign 02",
                        "userId": "3AAABLZtkPdCXic1dNAXpxblxIO2sR0pnbOWYGBhzhdNwON8NbKJoj2IPbClomEdRzNhQJrx64zZjl3WbzoofzjCmEH5gZcX7"
                    }
                ]
            }
        )
        sc = signclient_example
        sc.api_url =''
        sc.groups =[]
#        result = sc.get_users()


def test_get_groups(signclient_example):
    mock_get = MagicMock()
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
        sc = signclient_example
        sc.api_url =""
        result = sc.get_groups()
        assert result == {'default group': 'OZR8L8ZDql6m5', 'group 1': 'LBQBZLPrDk7Pn', 'group 2': 'tin31laZIb36L'}
