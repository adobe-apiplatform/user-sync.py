import pytest
import six

from user_sync.config import ConfigLoader
from user_sync.connector.directory import DirectoryConnector
from user_sync.rules import RuleProcessor


@pytest.fixture
def example_engine(default_args):
    config = ConfigLoader(default_args)
    rule_config = config.get_rule_options()
    return RuleProcessor(rule_config)

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


def test_read_desired_user_groups(example_engine, example_user, test_resources):

    dc = DirectoryConnector
    user = {'user@example.com': example_user}

    def dir_user_replacement(groups, extended_attributes, all_users):
        return six.itervalues(user)

    dc.load_users_and_groups = dir_user_replacement
    mappings = {
        'Test Group Admins 1': {
            'priority': 4,
            'roles': {'GROUP_ADMIN'},
            'groups': []
        },
        'Test Group Admins 2': {
            'priority': 1,
            'roles': {'ACCOUNT_ADMIN'},
            'groups': []
        },
    }
    assert example_engine.read_desired_user_groups({}, dc) is None
    assert example_engine.read_desired_user_groups(mappings, dc) is None


def test_skip_user(example_engine,example_user,test_resources):

    user = {'user@example.com': example_user}

    def dir_user_replacement(groups, extended_attributes, all_users):
        return six.itervalues(user)
    dc = DirectoryConnector
    dc.load_users_and_groups = dir_user_replacement
    mappings = {
        'Test Group Admins 1': {
            'priority': 4,
            'roles': {'GROUP_ADMIN'},
            'groups': []
        },
        'Test Group Admins 2': {
            'priority': 1,
            'roles': {'ACCOUNT_ADMIN'},
            'groups': []
        },
    }

    after_mapping_hook_text = 'skip_user'
    example_engine.options['after_mapping_hook'] = compile(after_mapping_hook_text, '<per-user after-mapping-hook>', 'exec')
    assert example_engine.read_desired_user_groups({}, dc) is None
    assert example_engine.read_desired_user_groups(mappings, dc) is None