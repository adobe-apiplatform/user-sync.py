import json
from unittest import mock

import pytest
from requests import Response

from user_sync.post_sync import PostSyncConnector
from user_sync.post_sync.connectors.sign_sync import SignClient, SignConnector
from user_sync.post_sync.manager import PostSyncData


@pytest.fixture
def example_user():
    return {
        'type': 'federatedID',
        'username': 'user@example.com',
        'domain': 'example.com',
        'email': 'user@example.com',
        'firstname': 'Example',
        'lastname': 'User',
        'groups': set(),
        'country': 'US',
    }


def test_add_umapi_user(example_user):
    email_id = 'user@example.com'
    post_sync_data = PostSyncData()
    post_sync_data.update_umapi_data(None, email_id, [], [], **example_user)
    assert post_sync_data.umapi_data[None][email_id] == example_user


def test_add_groups(example_user):
    post_sync_data = PostSyncData()
    email_id = 'user@example.com'
    example_user['groups'] = {'group1', 'group2', 'group3'}
    groups_add = ['group3', 'group4', 'group5']
    post_sync_data.update_umapi_data(None, email_id, groups_add, [], **example_user)
    assert post_sync_data.umapi_data[None][email_id]['groups'] == example_user['groups'] | set(groups_add)


def test_remove_groups(example_user):
    post_sync_data = PostSyncData()
    email_id = 'user@example.com'
    example_user['groups'] = {'group1', 'group2', 'group3'}
    groups_remove = ['group1', 'group2']
    post_sync_data.update_umapi_data(None, email_id, [], groups_remove, **example_user)
    assert post_sync_data.umapi_data[None][email_id]['groups'] == example_user['groups'] - set(groups_remove)


def test_add_remove_groups(example_user):
    post_sync_data = PostSyncData()
    email_id = 'user@example.com'
    example_user['groups'] = {'group1', 'group2', 'group3', 'group4', 'group5'}
    groups_add = ['group6']
    groups_remove = ['group1', 'group2']
    post_sync_data.update_umapi_data(None, email_id, groups_add, groups_remove, **example_user)
    delta_groups = example_user['groups'] | set(groups_add)
    delta_groups -= set(groups_remove)
    assert post_sync_data.umapi_data[None][email_id]['groups'] == delta_groups


@mock.patch('requests.get')
@mock.patch('user_sync.post_sync.connectors.sign_sync.client.SignClient._init')
def test_update_sign_users(mock_client, mock_get, example_user):
    def mock_response(data):
        r = Response()
        r.status_code = 200
        r._content = json.dumps(data).encode()
        return r
    #     user_list = mock_response({'userInfoList': [{"userId": "123"}, {"userId": "456"}]})
    user_list = mock_response({'userInfoList': [{"userId": "123"}]})
    user_one = mock_response({'userStatus': 'ACTIVE', 'email': 'user@example.com'})
    # user_two = mock_response({'userStatus': 'ACTIVE', 'email': 'user2@example.com'})
    mock_get.side_effect = [user_list, user_one]
    client_config = {
                'console_org': None,
                'host': 'api.na2.echosignstage.com',
                'key': 'allsortsofgibberish1234567890',
                'admin_email': 'brian.nickila@gmail.com'
            }
    sign_client = SignClient(client_config)
    sign_client.api_url = "whatever"
    # sign_users = sign_client.get_users()
    # assert sign_users is not None
    connector_config = {
        'sign_orgs': [{'console_org': None,
        'host': 'api.na2.echosignstage.com',
        'key': 'allsortsofgibberish1234567890',
        'admin_email': 'brian.nickila@gmail.com'}],
        'entitlement_groups': ['group1']
    }
    sign_connector = SignConnector(connector_config)
    assert isinstance(sign_connector, SignConnector)
    example_user['email'] = 'User@example.com'
    assert example_user['email'].lower() != example_user['email']
    #define replacement should_sync
    def hello(cls, umapi_user, sign_user, org_name):
        print('x')
        #assert sign_user not None
    sign_connector.should_sync = hello
    sign_connector.update_sign_users(example_user, sign_client, None)
    # assert sign_users['user@example.com']['email'] == 'user@example.com'
    # sign_connector.should_sync replacement method
