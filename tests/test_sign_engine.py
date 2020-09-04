from unittest.mock import MagicMock

import pytest
import six
from unittest import mock

from user_sync.connector.directory import DirectoryConnector
from user_sync.engine.sign import SignSyncEngine
from user_sync.connector.connector_sign import SignConnector
from sign_client.client import SignClient

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

    # replace the call to load directory groups and users with the example user dict. this dict will then be modified
    # by other methods in the engine/sign.py which are almost identical to the same methods in engine/umapi.py right now
    # these methods should be altered for sign-specific usage - for example, there's no need to specify an identity
    # type for sign-syncing purposes, but it has been left in there so that the code can run
    dc.load_users_and_groups = dir_user_replacement
    directory_users = example_engine.read_desired_user_groups({'directory_group': 'adobe_group'}, dc)
    assert directory_users is not None


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

def test_get_directory_user_key(example_engine, example_user):
    tem_user = example_engine.get_directory_user_key(example_user)
    assert tem_user is not None


@pytest.fixture
def sign_user_1():
    return {
        'firstName': 'Dev',
        'lastName': 'One',
        'email': 'test1@dev-sign-02.com',
        'company': 'Dev Sign 02',
        'initials': 'DO',
        'channel': 'AdobeAccountsChannel',
        'account': 'test@xyz.com',
        'groups': 'Default Group',
        'groupId': 'abcdef',
        'accountType': 'GLOBAL',
        'capabilityFlags': ['CAN_SEND', 'CAN_SIGN', 'CAN_REPLACE_SIGNER'],
        'userStatus': 'ACTIVE',
        'optIn': 'NO',
        'userId': 'testiddssd',
        'roles': ['NORMAL_USER']
    }


def test_should_sync(example_engine, input_umapi_user, sign_user_1):

    signUser = example_engine.should_sync(input_umapi_user, None, None)
    assert not signUser

    input_umapi_user['type'] = 'federatedID'
    example_engine.identity_types = ['adobeID']
    umapiUser = example_engine.should_sync(input_umapi_user, sign_user_1, None)
    assert not umapiUser

    input_umapi_user['groups'] = {'Default Group'}
    umapiGroup = example_engine.should_sync(input_umapi_user,sign_user_1,None)
    assert not umapiGroup

    input_umapi_user['groups'] = {'signgroup'}
    input_umapi_user['type'] = 'federatedID'
    example_engine.identity_types = ['adobeID', 'enterpriseID', 'federatedID']
    valid_umapi_status = example_engine.should_sync(input_umapi_user,sign_user_1,None)
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
                        'domain': 'dev-sign-02.com', 'email': 'SignUser4@dev-sign-02.com',
                        'firstname': 'Sign', 'lastname': 'User 4',
                        'groups': {'sign_group_one', '_admin_sign_group_one'},
                        'country': 'US'}}

    user =  {'firstName': 'Sign',
             'lastName': 'User 4', 'email': 'signuser4@dev-sign-02.com',
             'company': 'Dev Sign 02', 'initials': 'SU', 'channel': 'AdobeAccountsChannel',
             'account': 'shasijena09@gmail.com', 'group': 'Default Group',
             'groupId': '3AAABLZtkPdAH9sz1KbI8GSydrljH2bmhtjOwhNHD9NnnaEZbGyzjGWiiDkEOGzzF5AVZDCXyBwDiebPyEY-OZR8L8ZDql6m5',
             'accountType': 'GLOBAL', 'capabilityFlags': ['CAN_SEND', 'CAN_SIGN', 'CAN_REPLACE_SIGNER'],
             'userStatus': 'ACTIVE', 'optIn': 'NO', 'userId': '3AAABLZtkPdC_NRQleh2ISf0LDXotehwP0pdQ9a3zs-igC5JKf8SGaFsauj8LmOSa8OZmpbSeK0TriyDa2LS-t-XCSqDBIuVp',
             'roles': ['NORMAL_USER']}

    # mock get_users()
    def dir_user_replace():
        return user

    sc.get_users = dir_user_replace
    example_engine.update_sign_users(directory_users,sc,None)
