import uuid

import pytest

from user_sync.credentials import *
from user_sync.error import AssertionException


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




