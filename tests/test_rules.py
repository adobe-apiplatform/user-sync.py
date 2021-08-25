from unittest.mock import MagicMock

import pytest

from user_sync.rules import RuleProcessor


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
        'source_attributes': {
            'email': 'user@example.com',
            'identity_type': None,
            'username': 'user@example.com',
            'domain': 'example.com',
            'givenName': 'Example',
            'sn': 'User',
            'c': 'US'}
    }


def test_skip_user(example_user):
    # Fake directory connector
    dc = MagicMock()
    dc.load_users_and_groups.return_value = [example_user]

    def run_extension(text):
        rp = RuleProcessor({})
        after_mapping_hook_text = text
        rp.options['after_mapping_hook'] = compile(
            after_mapping_hook_text, '<per-user after-mapping-hook>', 'exec')
        rp.read_desired_user_groups({}, dc)
        return rp

    state = run_extension('pass')
    user_key = state.get_directory_user_key(example_user)
    assert user_key in state.directory_user_by_user_key
    assert user_key in state.filtered_directory_user_by_user_key
    assert state.skipped_user_count == 0

    state = run_extension('skip_user()')
    user_key = state.get_directory_user_key(example_user)
    assert user_key not in state.directory_user_by_user_key
    assert user_key not in state.filtered_directory_user_by_user_key
    assert state.skipped_user_count == 1
