import logging
from unittest.mock import MagicMock

import pytest
import six

from sign_client.client import SignClient
from user_sync.connector.connector_sign import SignConnector
from user_sync.connector.directory import DirectoryConnector
from user_sync.engine.sign import SignSyncEngine

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


@pytest.fixture
def input_umapi_user():
    return {
        'type': 'adobeID',
        'username': 'test@adobe.com',
        'domain': 'adobe.com',
        'email': 'test@adobe.com',
        'firstname': 'test',
        'lastname': 'user',
        'groups': {'all apps'},
        'country': 'US'
    }

def test_admin_role_mapping():
    sync_config = MagicMock()
    sync_config.get_list.return_value = [{'sign_role': 'ACCOUNT_ADMIN', 'adobe_groups': ['sign_group_one']}]
    returnValue = SignSyncEngine._admin_role_mapping(sync_config)
    assert returnValue == {None: {'sign_group_one': {'ACCOUNT_ADMIN'}}}

def test__groupify():
    processed_groups = SignSyncEngine._groupify(['group1', 'group2'])
    assert processed_groups[None] == ['group1', 'group2']



@pytest.fixture
def sign_user():
    return {
        'email': 'test1@dev-sign-02.com',
        'groups': 'Default Group',
        'userStatus': 'ACTIVE',
        'userId': 'testiddssd',
        'roles': ['NORMAL_USER']
    }


def test_should_sync(example_engine, input_umapi_user, sign_user):

    signUser = example_engine.should_sync(input_umapi_user, None, None)
    assert not signUser

    input_umapi_user['type'] = 'federatedID'
    example_engine.identity_types = ['adobeID']
    umapiUser = example_engine.should_sync(input_umapi_user, sign_user, None)
    assert not umapiUser

    input_umapi_user['groups'] = {'Default Group'}
    umapiGroup = example_engine.should_sync(input_umapi_user,sign_user,None)
    assert not umapiGroup

    input_umapi_user['groups'] = {'signgroup'}
    input_umapi_user['type'] = 'federatedID'
    example_engine.identity_types = ['adobeID', 'enterpriseID', 'federatedID']
    valid_umapi_status = example_engine.should_sync(input_umapi_user,sign_user,None)
    assert valid_umapi_status is True

def test_roles_match():
    resolved_roles = ['ACCOUNT_ADMIN', 'GROUP_ADMIN', 'NORMAL_USER']
    sign_roles = ['ACCOUNT_ADMIN', 'GROUP_ADMIN', 'NORMAL_USER']
    assert SignSyncEngine.roles_match(resolved_roles, sign_roles) is True

    resolved_roles = ['GROUP_ADMIN', 'NORMAL_USER', 'ACCOUNT_ADMIN']
    sign_roles = ['ACCOUNT_ADMIN', 'GROUP_ADMIN', 'NORMAL_USER']
    assert SignSyncEngine.roles_match(resolved_roles, sign_roles) is True

    resolved_roles = []
    sign_roles = []
    assert SignSyncEngine.roles_match(resolved_roles, sign_roles) is True

    resolved_roles = ['normal_user']
    sign_roles = [ 'NORMAL_USER']
    assert SignSyncEngine.roles_match(resolved_roles, sign_roles) is False

    resolved_roles = ['NORMAL_USER','ACCOUNT_ADMIN']
    sign_roles = ['GROUP_ADMIN', 'NORMAL_USER']
    assert SignSyncEngine.roles_match(resolved_roles, sign_roles) is False


def test_resolve_new_roles(input_umapi_user):
    role_mapping = {'all apps': {'ACCOUNT_ADMIN'}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert roles == ['ACCOUNT_ADMIN']

    role_mapping = {'all apps': {'GROUP_ADMIN'}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert roles == ['GROUP_ADMIN']

    role_mapping = {'all apps': {'ACCOUNT_ADMIN', 'ACCOUNT_ADMIN'}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert roles == ['ACCOUNT_ADMIN']

    role_mapping = {'all apps': {}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert roles == ['NORMAL_USER']

    role_mapping = {'all apps': {'ACCOUNT_ADMIN', 'GROUP_ADMIN'}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert set(roles) == {'GROUP_ADMIN', 'ACCOUNT_ADMIN'}


def test_update_sign_users(example_engine):
    sc = SignSyncEngine.connectors = {}
    client_config = {
        'console_org': None,
        'host': 'api.na2.echosignstage.com',
        'key': 'allsortsofgibberish1234567890',
        'admin_email': 'brian.nickila@gmail.com'
    }
    sign_client = SignClient(client_config)
    connector_config = {
        'console_org': 'testorg',
        'host': 'api.na2.echosignstage.com',
        'key': 'allsortsofgibberish1234567890',
        'admin_email': 'brian.nickila@gmail.com',
        'sign_orgs': [client_config],
        'entitlement_groups': ['group1']
    }
    sc = SignConnector(connector_config)
    directory_users = {'federatedID,signuser4@dev-sign-02.com,':
                       {'type': 'federatedID',
                        'username': 'SignUser4@dev-sign-02.com',
                        'domain': 'dev-sign-02.com',
                        'email': 'SignUser4@dev-sign-02.com',
                        'firstname': 'Sign',
                        'lastname': 'User 4',
                        'groups': {'sign_group_one'},
                        'country': 'US'}}

    user =  {
             'email': 'signuser4@dev-sign-02.com',
             'company': 'Dev Sign 02',
             'account': 'shasijena09@gmail.com',
             'group': 'Default Group',
             'accountType': 'GLOBAL',
             'userStatus': 'ACTIVE',
             'roles': ['NORMAL_USER']}

    # mock get_users()
    def dir_user_replace():
        return user

    sc.get_users = dir_user_replace
    example_engine.update_sign_users(directory_users,sc,None)
