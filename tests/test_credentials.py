import keyrings
import pytest
import uuid
from user_sync.error import AssertionException
from user_sync.credentials import CredentialManager
import user_sync.credentials
import keyring


def test_set():
    identifier = 'TestId'
    value = 'TestValue'
    CredentialManager().set(identifier, value)
    check_password = CredentialManager().get(identifier)
    assert check_password == value


def test_set_method2():
    identifier = 'TestId4'
    x = ""
    for i in range(500):
        x += str(uuid.uuid4())
    value = x

    if isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring):
        keyring.set_keyring(keyrings.cryptfile.cryptfile.CryptFileKeyring())
        check_password = CredentialManager().get(identifier)
        assert check_password == value


def test_set_method3():
    identifier = 'TestId5'
    x = ""
    for i in range(500):
        x += str(uuid.uuid4())
    value = x
    if isinstance(keyring.get_keyring(), keyring.backends.Windows.WinVaultKeyring):
        with pytest.raises(AssertionException):
            CredentialManager().set(identifier, value)
