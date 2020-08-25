import pytest
import six

from user_sync.connector.directory import DirectoryConnector
from user_sync.engine.sign import SignSyncEngine


@pytest.fixture
def example_engine(modify_root_config, sign_config_file):
    modify_root_config(['post_sync', 'modules'], 'sign_sync')
    modify_root_config(['post_sync', 'connectors'], sign_config_file)
    args = {'config_filename': sign_config_file}
    args['entitlement_groups'] = 'signgroup'
    args['sign_orgs'] = []
    return SignSyncEngine(args)


def test_load_users_and_groups(example_engine, example_user):
    dc = DirectoryConnector

    user = {'user@example.com': example_user}

    def dir_user_replacement(groups, extended_attributes, all_users):
        return six.itervalues(user)

    dc.load_users_and_groups = dir_user_replacement
    example_engine.read_desired_user_groups({'directory_group': 'adobe_group'}, dc)
    # if the user has an email attribute, the method will index the user dict by email, which is how it's passed
    # in in this test anyway
    assert example_engine.directory_user_by_user_key == user


def test_get_directory_user_key(example_engine, example_user):
    # user = {'user@example.com': example_user}
    # if the method is passed a dict with an email, it should return the email key
    assert example_engine.get_directory_user_key(example_user) == example_user['email']
    # if the user object passed in has no email value, it should return None
    assert example_engine.get_directory_user_key({'': {'username': 'user@example.com'}}) is None
