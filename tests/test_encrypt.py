import os
import shutil

import pytest

from user_sync.encryption import Encryption
from user_sync.error import AssertionException





def test_salt(private_key):
    password = 'password'
    assert Encryption.encrypt(private_key, password, secure_salt=True)
    assert Encryption.decrypt(private_key, password)

def test_create_key(private_key):
    password = 'password'
    invalid_password = 'wrong_password'
    key = b'\xdf\xbc6\x95\x96\xe0N\xdd\x84\x82\x8eP\xef#GE\x82r\x98\xe8I\x1a\x13D\x16/U\x85\xd7\xc5Ho'
    assert Encryption.get_key(password) == key
    assert Encryption.get_key(invalid_password) != key


def test_encrypt_file(private_key, encrypted_key):
    password = 'password'
    assert Encryption.encrypt(private_key, password)
    # Try encrypting an already encrypted file
    with pytest.raises(AssertionException, match='File has already been encrypted.'):
        Encryption.encrypt(private_key, password)


def test_decrypt_file(encrypted_key, private_key):
    password = 'password'
    invalid_password = 'wrong_password'
    # Try using the wrong password
    with pytest.raises(AssertionException, match='Password was incorrect.'):
        Encryption.decrypt_file(encrypted_key, invalid_password)
    # Try using an already decrypted file
    with pytest.raises(AssertionException, match='File has not been encrypted.'):
        Encryption.decrypt_file(private_key, password)
    assert Encryption.decrypt_file(encrypted_key, password)


def test_encrypt_and_decrypt(private_key):
    password = 'password'
    with open(private_key, 'rb') as file:
        original_data = file.read()
    Encryption.encrypt(private_key, password)
    with open(private_key, 'rb') as file:
        encrypted_data = file.read()
    Encryption.decrypt_file(private_key, password)
    with open(private_key, 'rb') as file:
        decrypted_data = file.read()
    assert original_data == decrypted_data
    assert encrypted_data != original_data and encrypted_data != decrypted_data
