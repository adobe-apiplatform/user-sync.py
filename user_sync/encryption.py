from Crypto.PublicKey import RSA

from user_sync.error import AssertionException


def read_key(filename):
    with open(filename, 'r') as f:
        return f.read()


def write_key(data, filename):
    with open(filename, 'w') as f:
        f.write(data)


def encrypt_file(passphrase, filename):
    data = read_key(filename)
    return encrypt(passphrase, data)


def decrypt_file(passphrase, filename):
    data = read_key(filename)
    return decrypt(passphrase, data)


def encrypt(passphrase, data):
    try:
        key = RSA.import_key(data, passphrase=None)
        return RSA.RsaKey.export_key(key, format='PEM', passphrase=passphrase, pkcs=8).decode('ascii')
    except (ValueError, IndexError, TypeError) as e:
        if contains_phrase(str(e), "post boundary", "rsa key format", "out of range"):
            raise AssertionException(
                '{0} - Error while processing data. Data may not be in RSA format or is corrupt.'.format(str(e)))
        elif contains_phrase(str(e), "no passphrase available"):
            raise AssertionException(
                '{0} - Error while processing data. Data is already encrypted.'.format(str(e)))
        raise


def decrypt(passphrase, data):
    try:
        decrypted_key = RSA.import_key(data, passphrase)
        return decrypted_key.export_key('PEM').decode('ascii')
    except (ValueError, IndexError) as e:
        if contains_phrase(str(e), "padding is incorrect"):
            raise AssertionException('Password was incorrect.')
        elif contains_phrase(str(e), "index out of range", "format is not supported"):
            raise AssertionException(
                '{0} - Error while while processing encrypted data. '
                'Data may not be in RSA format or is corrupt.'.format(str(e)))
        raise


def contains_phrase(result, *args):
    return True in {x.lower() in result.lower() for x in args}

def is_encryptable(data):
    try:
        encrypt("pass", data)
        return True
    except Exception:
        return False


