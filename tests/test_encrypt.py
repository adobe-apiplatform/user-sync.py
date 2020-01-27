import os
import shutil

import pytest

import user_sync.encrypt
from user_sync.error import AssertionException





def test_create_key(private_key):
    password = 'password'
    invalid_password = 'wrong_password'
    encryption = user_sync.encrypt.Encryption(private_key, password)
    key = b'\xdf\xbc6\x95\x96\xe0N\xdd\x84\x82\x8eP\xef#GE\x82r\x98\xe8I\x1a\x13D\x16/U\x85\xd7\xc5Ho'
    assert encryption.create_key(password) == key
    assert encryption.create_key(invalid_password) != key


def test_encrypt_file(private_key, encrypted_key):
    password = 'password'
    encryption = user_sync.encrypt.Encryption(private_key, password)
    assert encryption.encrypt_file()
    # Try encrypting an already encrypted file
    encryption = user_sync.encrypt.Encryption(encrypted_key, password)
    with pytest.raises(AssertionException, match='File has already been encrypted.'):
        encryption.encrypt_file()


def test_decrypt_file(encrypted_key, private_key):
    password = 'password'
    invalid_password = 'wrong_password'
    # Try using the wrong password
    decryption = user_sync.encrypt.Encryption(encrypted_key, invalid_password)
    with pytest.raises(AssertionException, match='Password was incorrect.'):
        decryption.decrypt_file()
    # Try using an already decrypted file
    decryption = user_sync.encrypt.Encryption(private_key, password)
    with pytest.raises(AssertionException, match='File has not been encrypted.'):
        decryption.decrypt_file()
    decryption = user_sync.encrypt.Encryption(encrypted_key, password)
    assert decryption.decrypt_file()


def test_encrypt_and_decrypt(private_key):
    password = 'password'
    with open(private_key, 'rb') as file:
        original_data = file.read()
    encryption = user_sync.encrypt.Encryption(private_key, password)
    encryption.encrypt_file()
    with open(private_key, 'rb') as file:
        encrypted_data = file.read()
    decryption = user_sync.encrypt.Encryption(private_key, password)
    decryption.decrypt_file()
    with open(private_key, 'rb') as file:
        decrypted_data = file.read()
    assert original_data == decrypted_data
    assert encrypted_data != original_data and encrypted_data != decrypted_data
