import pytest
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
