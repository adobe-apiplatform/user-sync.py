import pytest
from user_sync.encryption import Encryption
from user_sync.error import AssertionException


def test_encrypt(private_key):
    passphrase = 'password'
    Encryption.encrypt(passphrase, private_key)
    with open(private_key, 'r') as f:
        data = f.read()
    assert 'DEK-Info: DES-EDE3-CBC,' in data
    with open(private_key, 'w') as f:
        f.write('invalid data')
    with pytest.raises(AssertionException):
        Encryption.encrypt(passphrase, private_key)
    with open(private_key, 'w') as f:
        f.write('')
    with pytest.raises(AssertionException):
        Encryption.encrypt(passphrase, private_key)


def test_decrypt(private_key, encrypted_key):
    passphrase = 'password'
    Encryption.decrypt(passphrase, encrypted_key)
    with open(private_key, 'r') as f:
        original = f.read()
    with open(encrypted_key, 'r') as f:
        decrypted = f.read()
    assert decrypted == original
    passphrase = 'wrong-password'
    with pytest.raises(AssertionException):
        Encryption.decrypt(passphrase, encrypted_key)
    with open(encrypted_key, 'w') as f:
        f.write('invalid data')
    with pytest.raises(AssertionException):
        Encryption.decrypt(passphrase, encrypted_key)


def test_encrypt_and_decrypt(private_key):
    with open(private_key, 'r') as f:
        original = f.read()
    passphrase = 'password'
    Encryption.encrypt(passphrase, private_key)
    with open(private_key, 'r') as f:
        encrypted = f.read()
    assert encrypted != original
    Encryption.decrypt(passphrase, private_key)
    with open(private_key, 'r') as f:
        output = f.read()
    assert output == original
