import re
from Crypto.PublicKey import RSA
from user_sync.error import AssertionException


def read_key(pk_file):
    with open(pk_file, 'r') as f:
        return f.read()

def write_key(data, pk_file):
    with open(pk_file, 'w') as f:
        f.write(data)

def encrypt(passphrase, pk_file):
    try:
        data = read_key(pk_file)
        key = RSA.import_key(data, passphrase=None)
        return RSA.RsaKey.export_key(key, format='PEM', passphrase=passphrase, pkcs=8).decode('ascii')
    except (ValueError, IndexError, TypeError) as e:
        if re.search('(post boundary|rsa key format|out of range)', str(e), flags=re.I):
            msg = 'Error: {0} while processing {1}\nFile may be invalid or corrupt.'.format(str(e), pk_file)
            raise AssertionException(msg)
        if re.search('(no passphrase available)', str(e), flags=re.I):
            msg = 'Error: {0} while processing {1}\nFile is already encrypted.'.format(str(e), pk_file)
            raise AssertionException(msg)
        raise

def decrypt(passphrase, pk_file):
    try:
        encrypted_key = read_key(pk_file)
        decrypted_key = RSA.import_key(encrypted_key, passphrase)
        return decrypted_key.export_key('PEM').decode('ascii')
    except (ValueError, IndexError) as e:
        if str(e) == 'Padding is incorrect.':
            raise AssertionException('Password was incorrect.')
        if re.search('(index out of range|format is not supported)', str(e), flags=re.I):
            msg = 'Error: {0} while processing {1}\nFile may be invalid or corrupt.'.format(str(e), pk_file)
            raise AssertionException(msg)
        raise

