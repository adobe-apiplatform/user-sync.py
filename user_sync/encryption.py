from Crypto.PublicKey import RSA
from user_sync.error import AssertionException


class Encryption:

    @staticmethod
    def read_key(pk_file):
        with open(pk_file, 'r') as data:
            return data.read()

    @staticmethod
    def encrypt(passphrase, pk_file):
        # Get the original unencrypted key from read_key() and set it to key
        try:
            data = Encryption.read_key(pk_file)
            key = RSA.import_key(data, passphrase=None)
            # Convert the key to an encrypted key using export_key() and passing in the passphrase
            encrypted_key = RSA.RsaKey.export_key(
                key, format='PEM',
                passphrase=passphrase,
                pkcs=8
            )
            Encryption.write_key(encrypted_key, pk_file)
        except ValueError as e:
            if str(e) == "PEM is encrypted, but no passphrase available":
                raise AssertionException('File has already been encrypted.')

    @staticmethod
    def write_key(data, pk_file):
        with open(pk_file, 'w') as f:
            f.write(data)

    @staticmethod
    def decrypt(passphrase, pk_file):
        try:
            encrypted_key = Encryption.read_key(pk_file)
            if 'DEK-Info: DES-EDE3-CBC,' in encrypted_key:
                decrypted_key = RSA.import_key(encrypted_key, passphrase)
                data = decrypted_key.export_key('PEM')
                Encryption.write_key(data, pk_file)
            else:
                raise AssertionException('File has not been encrypted.')
        except ValueError as e:
            if str(e) == 'Padding is incorrect.':
                raise AssertionException('Password was incorrect.')
