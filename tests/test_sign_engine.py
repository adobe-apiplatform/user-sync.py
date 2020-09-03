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


def test__groupify():
    processed_groups = SignSyncEngine._groupify(['group1','group2'])
    assert processed_groups[None] == ['group1', 'group2']
    assert isinstance(processed_groups[None],list)


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
        'group': 'Default Group',
        'groupId': 'abcdef',
        'accountType': 'GLOBAL',
        'capabilityFlags': ['CAN_SEND', 'CAN_SIGN', 'CAN_REPLACE_SIGNER'],
        'userStatus': 'ACTIVE',
        'optIn': 'NO',
        'userId': 'testiddssd',
        'roles': ['NORMAL_USER']
    }


def test_should_sync(example_engine, input_umapi_user, sign_user_1):
    temp_sign_user = example_engine.should_sync(input_umapi_user, sign_user_1, "Org_name")

def test_roles_match():
    resolved_roles = ['ACCOUNT_ADMIN', 'GROUP_ADMIN', 'NORMAL_USER']
    sign_roles = ['ACCOUNT_ADMIN', 'GROUP_ADMIN', 'NORMAL_USER']
    assert SignSyncEngine.roles_match(resolved_roles, sign_roles) == True

    resolved_roles = ['GROUP_ADMIN','NORMAL_USER','ACCOUNT_ADMIN']
    sign_roles = ['ACCOUNT_ADMIN', 'GROUP_ADMIN','NORMAL_USER']
    assert SignSyncEngine.roles_match(resolved_roles,sign_roles) ==True


def test_resolve_new_roles(input_umapi_user):
    role_mapping = {'all apps': {'ACCOUNT_ADMIN'}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert roles == ['ACCOUNT_ADMIN']

    role_mapping = {'all apps': {'ACCOUNT_ADMIN', 'GROUP_ADMIN'}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert roles == ['ACCOUNT_ADMIN', 'GROUP_ADMIN']

    role_mapping = {'all apps': {}}
    roles = SignSyncEngine.resolve_new_roles(input_umapi_user, role_mapping)
    assert roles == ['NORMAL_USER']


def test_update_sign_users(example_engine, example_user):
    Directory_user = "test@adobe.com"
    org_name = "Sign test"
    sc = SignSyncEngine.connectors = {}
    update_user = ""
    for temp in sc:
        update_user = example_engine.update_sign_users(Directory_user, temp, org_name)
    assert update_user is not None
