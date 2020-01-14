import base64
import uuid

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad

from user_sync.error import AssertionException


class Encryption:

    @staticmethod
    def read(pk_file):
        with open(pk_file, 'rb') as data:
            return data.read()

    @staticmethod
    def is_encrypted(key_file):
        # Checks file contents to determine if it was encrypted by this utility.
        # Crypo creates a binary encryption - so we can guess if it has been encrypted by checking.
        # This does NOT guarantee that a file is unencrypted in general - rather, it is a good guess.
        textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
        with open(key_file, "rb") as file:
            data = file.read()
        return bool(data.translate(None, textchars))

    @staticmethod
    def get_salt(secure=False):
        # Secure salt is generated based on mac address.  This means that if the key is moved from the machine,
        # it cannot be decrypted elsewhere.  The default behavior overrides this with a static salt, but the
        # secure feature is available on the command line.
        if secure:
            return base64.b64encode(str(uuid.getnode()).encode('utf-8'))
        return b'\xe5\x87\x8fa\xed\x0f\x01fl\x91\x05]bd\xd9C\x89\x90N\xbb\xc0\x06\xc3\x03[b8\x0eI\xbc\x12\xdb'

    @staticmethod
    def get_key(password, secure_salt=False):
        return PBKDF2(password, Encryption.get_salt(secure_salt), dkLen=32)

    @staticmethod
    def encrypt(pk_file, password, secure_salt=False):
        if not Encryption.is_encrypted(pk_file):
            cipher = AES.new(Encryption.get_key(password, secure_salt), AES.MODE_CBC)
            ciphered_data = cipher.encrypt(pad(Encryption.read(pk_file), AES.block_size))
            with open(pk_file, "wb") as file_out:
                file_out.write(cipher.iv)
                file_out.write(ciphered_data)
            return ciphered_data
        else:
            raise AssertionException('File has already been encrypted.')

    @staticmethod
    def decrypt(pk_file, password):
        try:
            return Encryption.decrypt_file(pk_file, password)
        except AssertionException:
            return Encryption.decrypt_file(pk_file, password, True)

    @staticmethod
    def decrypt_file(pk_file, password, secure_salt=False):
        with open(pk_file, 'rb') as file_in:
            iv = file_in.read(16)
            ciphered_data = file_in.read()
        try:
            cipher = AES.new(Encryption.get_key(password, secure_salt), AES.MODE_CBC, iv=iv)
            original_data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
            with open(pk_file, 'wb') as file:
                file.write(original_data)
            return original_data
        except ValueError as e:
            if e.args[0] == 'Data must be padded to 16 byte boundary in CBC mode':
                raise AssertionException('File has not been encrypted.')
            elif e.args[0] == 'Padding is incorrect.':
                raise AssertionException('Password was incorrect or secure salt was used on another machine.')
            else:
                raise AssertionException('Unknown error: ' + e.args[0])
