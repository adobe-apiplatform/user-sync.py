import pytest
import six

from user_sync.connector.directory import DirectoryConnector
from user_sync.engine.sign import SignSyncEngine
from user_sync.connector.connector_sign import SignConnector
import logging


@pytest.fixture
def example_engine(modify_root_config, sign_config_file):
    modify_root_config(['post_sync', 'modules'], 'sign_sync')
    modify_root_config(['post_sync', 'connectors'], sign_config_file)
    args = {'config_filename': sign_config_file}
    args['entitlement_groups'] = 'signgroup'
    args['sign_orgs'] = []
    args['create_new_users'] = True
    return SignSyncEngine(args)


def test_load_users_and_groups(example_engine, example_user):
    dc = DirectoryConnector

    user = {'user@example.com': example_user}

    def dir_user_replacement(groups, extended_attributes, all_users):
        return six.itervalues(user)

    # replace the call to load directory groups and users with the example user dict. this dict will then be modified
    # by other methods in the engine/sign.py which are almost identical to the same methods in engine/umapi.py right now
    # these methods should be altered for sign-specific usage - for example, there's no need to specify an identity
    # type for sign-syncing purposes, but it has been left in there so that the code can run
    dc.load_users_and_groups = dir_user_replacement
    directory_users = example_engine.read_desired_user_groups({'directory_group': 'adobe_group'}, dc)
    assert directory_users is not None


def test_insert_new_users(example_user):
    sign_engine = SignSyncEngine
    sign_connector = SignConnector
    umapi_user = example_user
    user_roles = ['NORMAL_USER']
    group_id = 'somemumbojumbohexadecimalstring'
    assignment_group = 'default group'
    insert_data = {
            "email": umapi_user['email'],
            "firstName": umapi_user['firstname'],
            "groupId": group_id,
            "lastName": umapi_user['lastname'],
            "roles": user_roles,
        }
    def insert_user(insert_data):
        pass
    sign_connector.insert_user = insert_user
    sign_engine.logger = logging.getLogger()
    sign_engine.insert_new_users(sign_engine, sign_connector, umapi_user, user_roles, group_id, assignment_group)
    assert True
    assert insert_data['email'] == 'user@example.com'
