from unittest import mock

import pytest

from sign_client.client import SignClient
from tests.util import MockResponse


@pytest.fixture
def example_client():
    return SignClient(host='api.echosign.com',
                      integration_key='3AAABLZtkPdD5io',
                      admin_email='user@example.com',
                      connection={},
                      )


def test_base_uri(example_client):
    with mock.patch('sign_client.client.requests') as mocked_requests:
        mocked_requests.get.return_value = MockResponse(body={'api_access_point': 'api_test_value/'})
        result = example_client.base_uri()
        assert result == 'api_test_value/api/rest/v5/'


def test_get_users(example_client):
    # pass through

    pass


def test_get_groups(example_client):
    # pass through

    pass
