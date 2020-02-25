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


def test_get_valid():
    identifier = 'TestId'
    value = 'TestValue'
    CredentialManager().set(identifier, value)
    test_credential = CredentialManager().get(identifier)
    assert value == test_credential
def test_set_method2():
    identifier = 'TestId2'
    x = ""
    for i in range(500):
        x += str(uuid.uuid4())
    value = x

    if isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring):
        keyring.set_keyring(keyrings.cryptfile.cryptfile.CryptFileKeyring())
        check_password = CredentialManager().get(identifier)
        assert check_password == value
    if isinstance(keyring.get_keyring(), keyring.backends.Windows.WinVaultKeyring):
        with pytest.raises(AssertionException):
            CredentialManager().set(identifier, value)

def test_get_not_valid():
    # This is an identifier which should not exist in your backed.
    identifier = 'DoesNotExist'
    # keyring.get_password returns None when it cannot find the identifier (such as the case of a typo). No exception
    # is thrown in this case. This case is handled in app.py, which will throw an AssertionException if
    # CredentialManager.get() returns None.
    assert CredentialManager().get(identifier) is None
