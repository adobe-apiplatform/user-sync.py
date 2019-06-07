import pytest
from user_sync.post_sync import manager


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
        manager.update_sync_data(email_id, 'umapi', [], [], **example_user)
        assert manager._SYNC_DATA_STORE[email_id.lower()]['umapi_data'] == example_user
