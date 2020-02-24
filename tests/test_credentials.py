import pytest
import uuid
from user_sync.error import AssertionException
from user_sync.credentials import CredentialManager


def test_set():
    identifier = 'TestId'
    value = 'TestValue'
    manager = CredentialManager()
    manager.set(identifier, value)
    check_password = manager.get(identifier)
    assert check_password == value


def test_get_valid():
    identifier = 'TestId'
    value = 'TestValue'
    CredentialManager().set(identifier, value)
    test_credential = CredentialManager().get(identifier)
    assert value == test_credential


def test_get_not_valid():
    # This is an identifier which should not exist in your backed.
    identifier = 'DoesNotExist'
    # keyring.get_password returns None when it cannot find the identifier (such as the case of a typo). No exception
    # is thrown in this case. This case is handled in app.py, which will throw an AssertionException if
    # CredentialManager.get() returns None.
    assert CredentialManager().get(identifier) is None
