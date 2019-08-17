import pytest
from user_sync.post_sync import manager
PostSyncManager = manager.PostSyncManager


@pytest.fixture
def example_user():
    return {
        'identity_type': 'federatedID',
        'username': 'user@example.com',
        'domain': 'example.com',
        'email': 'user@example.com',
        'firstname': 'Example',
        'lastname': 'User',
        'groups': [],
        'country': 'US',
    }


def test_add_umapi_user(example_user, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(manager, '_SYNC_DATA_STORE', {})
        email_id = 'user@example.com'
        PostSyncManager.update_sync_data(email_id, 'umapi_data', [], [], **example_user)
        assert manager._SYNC_DATA_STORE[email_id.lower()]['umapi_data'] == example_user


def test_add_groups(example_user, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(manager, '_SYNC_DATA_STORE', {})
        email_id = 'user@example.com'
        example_user['groups'] = ['group1', 'group2', 'group3']
        groups_add = ['group3', 'group4', 'group5']
        PostSyncManager.update_sync_data(email_id, 'umapi_data', groups_add, [], **example_user)
        assert sorted(manager._SYNC_DATA_STORE[email_id.lower()]['umapi_data']['groups']) == sorted(list(set(
            example_user['groups']) | set(groups_add)))


def test_remove_groups(example_user, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(manager, '_SYNC_DATA_STORE', {})
        email_id = 'user@example.com'
        example_user['groups'] = ['group1', 'group2', 'group3']
        groups_remove = ['group1', 'group2']
        PostSyncManager.update_sync_data(email_id, 'umapi_data', [], groups_remove, **example_user)
        assert sorted(manager._SYNC_DATA_STORE[email_id.lower()]['umapi_data']['groups']) == sorted(list(set(
            example_user['groups']) - set(groups_remove)))


def test_add_remove_groups(example_user, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(manager, '_SYNC_DATA_STORE', {})
        email_id = 'user@example.com'
        example_user['groups'] = ['group1', 'group2', 'group3', 'group4', 'group5']
        groups_add = ['group6']
        groups_remove = ['group1', 'group2']
        PostSyncManager.update_sync_data(email_id, 'umapi_data', groups_add, groups_remove, **example_user)
        delta_groups = list(set(example_user['groups']) | set(groups_add))
        delta_groups = list(set(delta_groups) - set(groups_remove))
        assert sorted(manager._SYNC_DATA_STORE[email_id.lower()]['umapi_data']['groups']) == sorted(delta_groups)
