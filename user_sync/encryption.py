from Crypto.PublicKey import RSA
from user_sync.error import AssertionException
from os.path import abspath


class Encryption:

    @staticmethod
    def read_key(pk_file):
        with open(pk_file, 'r') as f:
            return f.read()

    @staticmethod
    def encrypt(passphrase, pk_file):
        # Get the original unencrypted key from read_key() and set it to key
        try:
            data = Encryption.read_key(pk_file)
            key = RSA.import_key(data, passphrase=None)
            # Convert the key to an encrypted key using export_key() and passing in the passphrase
            encrypted_key = RSA.RsaKey.export_key(key, format='PEM', passphrase=passphrase, pkcs=8).decode('ascii')
            Encryption.write_key(encrypted_key, pk_file)
        except ValueError as e:
            if str(e) == "Not a valid PEM post boundary" or str(e) == "RSA key format is not supported":
                raise AssertionException('{0} is invalid.'.format(abspath(pk_file)))
            if str(e) == "PEM is encrypted, but no passphrase available":
                raise AssertionException('{0} has already been encrypted.'.format(abspath(pk_file)))
        except IndexError as e:
            if str(e) == "index out of range":
                raise AssertionException('{0} cannot be encrypted.'.format(abspath(pk_file)))

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
                return decrypted_key.export_key('PEM').decode('ascii')
            else:
                raise AssertionException('{0} has not been encrypted.'.format(abspath(pk_file)))
        except ValueError as e:
            if str(e) == 'Padding is incorrect.':
                raise AssertionException('Password was incorrect.')
