import uuid

import pytest

from user_sync.credentials import *
from user_sync.error import AssertionException


@pytest.fixture
def root_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'user-sync-config.yml')


@pytest.fixture
def ldap_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'connector-ldap.yml')


def test_nested_set(ldap_config_file):
    c = CredentialConfig(ldap_config_file)
    c.set_nested_key(['password'], {'secure': 'somethingverysecure'})
    r = c.get_nested_key(['password', 'secure'])
    assert r == 'somethingverysecure'
    print()


def test_retrieve_ldap_creds_valid(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    c = CredentialConfig(ldap_config_file)
    key_list = ['password']
    plaintext_cred = c.get_nested_key(key_list)
    c.store_key(key_list)
    secure_identifier = c.get_qualified_identifier(key_list)
    retrieved_plaintext_cred = c.retrieve_key(key_list)
    assert retrieved_plaintext_cred == plaintext_cred


def test_retrieve_ldap_creds_invalid(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    c = CredentialConfig(ldap_config_file)
    key_list = ['password']
    # if store_key has not been called previously, retrieve_key returns None
    assert c.retrieve_key(key_list) is None


def test_revert_valid(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    c = CredentialConfig(ldap_config_file)
    key_list = ['password']
    plaintext_cred = c.get_nested_key(key_list)
    c.store_key(key_list)
    reverted_plaintext_cred = c.revert_key(key_list)
    assert reverted_plaintext_cred == plaintext_cred


def test_revert_invalid(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    c = CredentialConfig(ldap_config_file)
    key_list = ['password']
    # assume store_key has not been called
    with pytest.raises(AssertionException):
        reverted_plaintext_cred = c.revert_key(key_list)


def test_retrieve_revert_ldap_valid(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    ldap = LdapCredentialConfig(ldap_config_file)
    assert not ldap.parse_secure_key(ldap.get_nested_key(['password']))
    unsecured_key = ldap.get_nested_key(['password'])
    ldap.store()
    with open(ldap_config_file) as f:
        data = yaml.load(f)
        assert ldap.parse_secure_key(data['password'])
    retrieved_key_dict = ldap.retrieve()
    assert retrieved_key_dict['password'] == unsecured_key
    reverted_creds_dict = ldap.revert()
    assert reverted_creds_dict['password'] == unsecured_key
    with open(ldap_config_file) as f:
        data = yaml.load(f)
        assert data['password'] == unsecured_key


def test_retrieve_revert_ldap_invalid(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    ldap = LdapCredentialConfig(ldap_config_file)
    assert not ldap.parse_secure_key(ldap.get_nested_key(['password']))
    unsecured_key = ldap.get_nested_key(['password'])
    # if store has not been previously called before retrieve and revert we can expect the following
    retrieved_key_dict = ldap.retrieve()
    assert retrieved_key_dict['password'] is None
    with pytest.raises(AssertionException):
        reverted_creds_dict = ldap.revert()


def test_retrieve_revert_umapi_valid(tmp_config_files):
    (_, _, umapi_config_file) = tmp_config_files
    umapi = UmapiCredentialConfig(umapi_config_file)
    # Using the org_id for assertions. The rest can be added in later if deemed necessary
    assert not umapi.parse_secure_key(umapi.get_nested_key(['enterprise', 'org_id']))
    unsecured_org_id = umapi.get_nested_key(['enterprise', 'org_id'])
    umapi.store()
    with open(umapi_config_file) as f:
        data = yaml.load(f)
        assert umapi.parse_secure_key(data['enterprise']['org_id'])
    retrieved_key_dict = umapi.retrieve()
    assert retrieved_key_dict['enterprise']['org_id'] == unsecured_org_id
    reverted_creds_dict = umapi.revert()
    assert reverted_creds_dict['enterprise']['org_id'] == unsecured_org_id
    with open(umapi_config_file) as f:
        data = yaml.load(f)
        assert data['enterprise']['org_id'] == unsecured_org_id


def test_set():
    identifier = 'TestId'
    value = 'TestValue'
    cm = CredentialManager()
    cm.set(identifier, value)


def test_get():
    identifier = 'TestId2'
    value = 'TestValue2'
    cm = CredentialManager()
    # Assume set works
    cm.set(identifier, value)
    assert cm.get(identifier) == value


def test_set_long():
    identifier = 'TestId3'
    cm = CredentialManager()
    value = "".join([str(uuid.uuid4()) for x in range(500)])

    if isinstance(keyring.get_keyring(), keyring.backends.Windows.WinVaultKeyring):
        with pytest.raises(AssertionException):
            cm.set(identifier, value)
    else:
        cm.set(identifier, value)
        assert cm.get(identifier) == value


def test_get_not_valid():
    # This is an identifier which should not exist in your backed.
    identifier = 'DoesNotExist'
    # keyring.get_password returns None when it cannot find the identifier (such as the case of a typo). No exception
    # is thrown in this case. This case is handled in app.py, which will throw an AssertionException if
    # CredentialManager.get() returns None.
    assert CredentialManager().get(identifier) is None


def test_config_store(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    ldap = LdapCredentialConfig(ldap_config_file)
    assert not ldap.parse_secure_key(ldap.get_nested_key(['password']))
    ldap.store()
    with open(ldap_config_file) as f:
        data = yaml.load(f)
        assert ldap.parse_secure_key(data['password'])


def test_config_store_key(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    ldap = LdapCredentialConfig(ldap_config_file)
    assert not ldap.parse_secure_key(ldap.get_nested_key(['password']))
    ldap.store_key(['password'])
    assert ldap.parse_secure_key(ldap.get_nested_key(['password']))


def test_config_store_key_none(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files
    ldap = LdapCredentialConfig(ldap_config_file)
    ldap.set_nested_key(['password'], [])
    with pytest.raises(AssertionException):
        ldap.store_key(['password'])

# def test_config_store_key_secured(tmp_config_files):
#     (_, ldap_config_file, _) = tmp_config_files
#     ldap = LdapCredentialConfig(ldap_config_file)
#     assert not ldap.parse_secure_key(ldap.get_nested_key(['password']))
#     ldap.store_key(['password'])
#     assert ldap.parse_secure_key(ldap.get_nested_key(['password']))
#     ldap.store_key(['password'])
#     assert ldap.parse_secure_key(ldap.get_nested_key(['password']))



