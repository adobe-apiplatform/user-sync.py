import re

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

from user_sync.error import AssertionException


class Encryption:
    def __init__(self, pk_file, password):
        self.pk_file = pk_file
        self.key = self.create_key(password)
        with open(pk_file, 'rb') as data:
            self.data = data.read()

    def is_encrypted(self, key_file):
        pattern = re.compile('\\\\x[A-aZ-z0-9]{0,3}\\\\')
        with open(key_file, "rb") as file:
            data = file.read()
        return len(pattern.findall(str(data))) > 100

    def create_key(self, password):
        salt = b'\xe5\x87\x8fa\xed\x0f\x01fl\x91\x05]bd\xd9C\x89\x90N\xbb\xc0\x06\xc3\x03[b8\x0eI\xbc\x12\xdb'
        return PBKDF2(password, salt, dkLen=32)

    def encrypt_file(self):
        if not self.is_encrypted(self.pk_file):
            cipher = AES.new(self.key, AES.MODE_CBC)
            ciphered_data = cipher.encrypt(pad(self.data, AES.block_size))
            with open(self.pk_file, "wb") as file_out:
                file_out.write(cipher.iv)
                file_out.write(ciphered_data)
            return ciphered_data
        else:
            raise AssertionException('File has already been encrypted.')

    def decrypt_file(self):
        with open(self.pk_file, 'rb') as file_in:
            iv = file_in.read(16)
            ciphered_data = file_in.read()
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
            original_data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
            with open(self.pk_file, 'wb') as file:
                file.write(original_data)
            return original_data
        except ValueError as e:
            if e.args[0] == 'Data must be padded to 16 byte boundary in CBC mode':
                raise AssertionException('File has not been encrypted.')
            elif e.args[0] == 'Padding is incorrect.':
                raise AssertionException('Password was incorrect.')
            else:
                raise AssertionException(e.args[0])
