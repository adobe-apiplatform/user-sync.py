import os
import uuid

import keyring
import pytest
import yaml

from user_sync import encryption
from user_sync.credentials import CredentialConfig, CredentialManager, Key, LdapCredentialConfig, UmapiCredentialConfig


def test_nested_set(test_resources):
    c = CredentialConfig(test_resources['ldap'])
    c.set_nested_key(['password'], {'secure': 'somethingverysecure'})
    r = c.get_nested_key(['password', 'secure'])
    assert r == 'somethingverysecure'


def test_retrieve_ldap_creds_valid(test_resources):
    c = CredentialConfig(test_resources['ldap'])
    key = Key(['password'])
    plaintext_cred = c.get_nested_key(key.key_path)
    c.store_key(key)
    retrieved_plaintext_cred = c.retrieve_key(key)
    assert retrieved_plaintext_cred == plaintext_cred


def test_retrieve_ldap_creds_invalid(test_resources):
    c = CredentialConfig(test_resources['ldap'])
    key = Key(['password'])
    # if store_key has not been called previously, retrieve_key returns None
    assert c.retrieve_key(key) is None


def test_revert_valid(test_resources):
    c = CredentialConfig(test_resources['ldap'])
    key = Key(['password'])
    plaintext_cred = c.get_nested_key(key.key_path)
    c.store_key(key)
    reverted_plaintext_cred = c.revert_key(key)
    assert reverted_plaintext_cred == plaintext_cred


def test_revert_invalid(test_resources):
    c = CredentialConfig(test_resources['ldap'])
    key = Key(['password'])
    # assume store_key has not been called
    assert c.revert_key(key) is None


def test_retrieve_revert_ldap_valid(test_resources):
    ldap = LdapCredentialConfig(test_resources['ldap'])
    assert not ldap.parse_secure_key(ldap.get_nested_key(['password']))
    unsecured_key = ldap.get_nested_key(['password'])
    ldap.store()
    with open(test_resources['ldap']) as f:
        data = yaml.safe_load(f)
        assert ldap.parse_secure_key(data['password'])
    retrieved_key_dict = ldap.retrieve()
    assert retrieved_key_dict['password'] == unsecured_key
    ldap.revert()
    with open(test_resources['ldap']) as f:
        data = yaml.safe_load(f)
        assert data['password'] == unsecured_key


def test_retrieve_revert_ldap_invalid(test_resources):
    ldap = LdapCredentialConfig(test_resources['ldap'])
    assert not ldap.parse_secure_key(ldap.get_nested_key(['password']))
    # if store has not been previously called before retrieve and revert we can expect the following
    retrieved_key_dict = ldap.retrieve()
    assert retrieved_key_dict == {}
    creds = ldap.revert()
    assert creds == {}


def test_retrieve_revert_umapi_valid(test_resources, modify_config):
    umapi_config_file = modify_config('umapi', ['enterprise', 'priv_key_path'], test_resources['priv_key'])
    umapi = UmapiCredentialConfig(umapi_config_file, auto=True)
    # Using the api_key for assertions. The rest can be added in later if deemed necessary
    assert not umapi.parse_secure_key(umapi.get_nested_key(['enterprise', 'client_id']))
    unsecured_api_key = umapi.get_nested_key(['enterprise', 'client_id'])
    umapi.store()
    with open(umapi_config_file, 'r') as f:
        data = yaml.safe_load(f)
        assert umapi.parse_secure_key(data['enterprise']['client_id'])
    retrieved_key_dict = umapi.retrieve()
    assert retrieved_key_dict['enterprise:client_id'] == unsecured_api_key
    umapi.revert()
    with open(umapi_config_file) as f:
        data = yaml.safe_load(f)
        assert data['enterprise']['client_id'] == unsecured_api_key


def test_credman_retrieve_revert_valid(test_resources, modify_config):
    umapi_config_file = modify_config('umapi', ['enterprise', 'priv_key_path'], test_resources['priv_key'])
    credman = CredentialManager(test_resources['umapi_root_config'], auto=True)
    with open(test_resources['ldap']) as f:
        data = yaml.safe_load(f)
        plaintext_ldap_password = data['password']
    with open(umapi_config_file) as f:
        data = yaml.safe_load(f)
        plaintext_umapi_api_key = data['enterprise']['client_id']
    credman.store()
    retrieved_creds = credman.retrieve()
    assert retrieved_creds[test_resources['ldap']]['password'] == plaintext_ldap_password
    assert retrieved_creds[umapi_config_file]['enterprise:client_id'] == plaintext_umapi_api_key
    # make sure the config files are still in secure format
    with open(test_resources['ldap']) as f:
        data = yaml.safe_load(f)
        assert data['password'] != plaintext_ldap_password
    with open(umapi_config_file) as f:
        data = yaml.safe_load(f)
        assert data['enterprise']['client_id'] != plaintext_umapi_api_key
    credman.revert()
    with open(test_resources['ldap']) as f:
        data = yaml.safe_load(f)
        assert data['password'] == plaintext_ldap_password
    with open(umapi_config_file) as f:
        data = yaml.safe_load(f)
        assert data['enterprise']['client_id'] == plaintext_umapi_api_key


def test_credman_retrieve_revert_invalid(test_resources, modify_config):
    umapi_config_file = modify_config('umapi', ['enterprise', 'priv_key_path'], test_resources['priv_key'])
    credman = CredentialManager(test_resources['umapi_root_config'])
    # if credman.store() has not been called first then we can expect the following
    retrieved_creds = credman.retrieve()
    assert retrieved_creds == {}
    creds = credman.revert()
    assert creds == {}


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
        with pytest.raises(Exception):
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


def test_config_store(test_resources):
    ldap = LdapCredentialConfig(test_resources['ldap'])
    key = Key(['password'])
    assert not ldap.parse_secure_key(ldap.get_nested_key(key.key_path))
    ldap.store()
    with open(test_resources['ldap']) as f:
        data = yaml.safe_load(f)
        assert ldap.parse_secure_key(data['password'])


def test_config_store_key(test_resources):
    ldap = LdapCredentialConfig(test_resources['ldap'])
    key = Key(['password'])
    assert not ldap.parse_secure_key(ldap.get_nested_key(key.key_path))
    ldap.store_key(key)
    assert ldap.parse_secure_key(ldap.get_nested_key(key.key_path))


def test_config_store_key_none(test_resources):
    ldap = LdapCredentialConfig(test_resources['ldap'])
    key = Key(['password'])
    ldap.set_nested_key(key.key_path, [])
    assert ldap.store_key(key) is None


def test_credman_encrypt_decrypt_key_path(test_resources, modify_config):
    umapi_config_file = modify_config('umapi', ['enterprise', 'priv_key_path'], test_resources['priv_key'])
    credman = CredentialManager(test_resources['umapi_root_config'], auto=True)
    with open(test_resources['priv_key']) as f:
        key_data = f.read()
        assert encryption.is_encryptable(key_data)
    credman.store()
    with open(test_resources['priv_key']) as f:
        key_data = f.read()
        assert not encryption.is_encryptable(key_data)
    credman.revert()
    with open(test_resources['priv_key']) as f:
        key_data = f.read()
        assert encryption.is_encryptable(key_data)


def test_credman_encrypt_decrypt_key_data(test_resources, modify_config):
    umapi_config_file = modify_config('umapi', ['enterprise', 'priv_key_path'], None)
    with open(test_resources['priv_key']) as f:
        key_data = f.read()
        umapi_config_file = modify_config('umapi', ['enterprise', 'priv_key_data'], key_data)
    credman = CredentialManager(test_resources['umapi_root_config'], auto=True)
    with open(umapi_config_file) as f:
        umapi_dict = yaml.safe_load(f)
        assert encryption.is_encryptable(umapi_dict['enterprise']['priv_key_data'])
    credman.store()
    with open(umapi_config_file) as f:
        umapi_dict = yaml.safe_load(f)
        assert not encryption.is_encryptable(umapi_dict['enterprise']['priv_key_data'])
    credman.revert()
    with open(umapi_config_file) as f:
        umapi_dict = yaml.safe_load(f)
        assert encryption.is_encryptable(umapi_dict['enterprise']['priv_key_data'])
