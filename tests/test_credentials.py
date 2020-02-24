import pytest
from user_sync.error import AssertionException
from user_sync.credentials import CredentialManager


def test_set():
    identifier = 'TestId'
    value = 'TestValue'
    manager = CredentialManager()
    CredentialManager.set(manager, identifier, value)
    check_password = CredentialManager.get(manager, identifier)
    assert check_password == value


def test_set_method2():
    identifier = 'TestId4'
    # value = 'extraLongPassword'
    # for x in range(20):
    #     value = value+value
    x = ""
    for i in range(500):
        x += str(uuid.uuid4())

    with pytest.raises(AssertionException):
        manager = CredentialManager()
        CredentialManager.set(manager, identifier, value)




