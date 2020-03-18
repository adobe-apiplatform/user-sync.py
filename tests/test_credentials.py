import os
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


def test_retrieve_ldap_creds_valid(ldap_config_file):
    c = CredentialConfig(ldap_config_file)
    plaintext_cred = c.get_nested_key(['password'])
    key_list = ['password']
    c.store_key(key_list)
    secure_identifier = c.get_qualified_identifier(['password'])
    retrieved_key_dict = c.retrieve_key(key_list)
    assert retrieved_key_dict[secure_identifier] == plaintext_cred


def test_retrieve_ldap_creds_invalid(ldap_config_file):
    c = CredentialConfig(ldap_config_file)
    key_list = ['password']
    # if the key is never stored, the retrieve command will raise an AssertionException because
    # parse_secure_key returns None
    with pytest.raises(AssertionException):
        c.retrieve_key(key_list)


def test_revert(ldap_config_file):
    c = CredentialConfig(ldap_config_file)
    plaintext_cred = c.get_nested_key(['password'])
    key_list = ['password']
    c.store_key(key_list)
    secure_identifier = c.get_qualified_identifier(['password'])
    reverted_key_dict = c.retrieve_key(key_list, revert=True)
    assert reverted_key_dict['password'] == plaintext_cred

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


