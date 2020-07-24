from unittest import mock

import pytest
from requests import Response


from user_sync.error import AssertionException
from sign_client.client import SignClient
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
@mock.patch('sign_client.client.SignClient._init')
def test_assertion_exception_sucess(mock_client, mock_get):

    mock_response = Response()
    mock_response.status_code = 400
    mock_get.return_value = mock_response

    config = {
        'console_org': None,
        'host': 'api.na2.echosignstage.com',
        'key': 'allsortsofgibberish1234567890',
        'admin_email': 'admin@admin.com'
    }

    sc = SignClient(config)
    sc.api_url = "example.com"

    with pytest.raises(AssertionException):
        sc.base_uri()

    with pytest.raises(AssertionException):
        sc.get_users()

    with pytest.raises(AssertionException):
        sc.get_groups()