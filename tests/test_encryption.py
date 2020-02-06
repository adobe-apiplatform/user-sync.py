import pytest
from user_sync.encryption import *
from user_sync.error import AssertionException


def test_encrypt(private_key, encrypted_key):
    passphrase = 'password'
    data = encrypt(passphrase, private_key)
    assert 'DEK-Info: DES-EDE3-CBC,' in data
    with pytest.raises(AssertionException):
        encrypt(passphrase, encrypted_key)
    with open(private_key, 'w') as f:
        f.write('invalid data')
    with pytest.raises(AssertionException):
        encrypt(passphrase, private_key)
    with open(private_key, 'w') as f:
        f.write('')
    with pytest.raises(AssertionException):
        encrypt(passphrase, private_key)


def test_decrypt(private_key, encrypted_key):
    passphrase = 'password'
    with open(private_key, 'r') as f:
        original = f.read()
    decrypted = decrypt(passphrase, encrypted_key)
    assert decrypted == original
    passphrase = 'wrong-password'
    with pytest.raises(AssertionException):
        decrypt(passphrase, encrypted_key)
    with open(encrypted_key, 'w') as f:
        f.write('invalid data')
    with pytest.raises(AssertionException):
        decrypt(passphrase, encrypted_key)


def test_encrypt_and_decrypt(private_key):
    with open(private_key, 'r') as f:
        original = f.read()
    passphrase = 'password'
    encrypted = encrypt(passphrase, private_key)
    assert encrypted != original
    decrypted = decrypt(passphrase, private_key)
    assert decrypted == original
