from Crypto.PublicKey import RSA


# Create a class that
#   1. opens private.key => returns
#   2. encrypts key using RSA with passphrase from click
#   3. writes the encrypted key onto the original private.key file
#   4. decrypts key (if encrypted and passphrase matches)

class RsaEncrypt:

    @staticmethod
    def read_key(pk_file):
        with open(pk_file, 'rb') as f:
            return f.read()
            # return RSA.import_key(data, passphrase=None)

    @staticmethod
    def encrypt_key(passphrase, pk_file):
        # Get the original unencrypted key from read_key() and set it to key
        data = RsaEncrypt.read_key(pk_file)
        key = RSA.import_key(data, passphrase=None)

        # Convert the key to an encrypted key using export_key() and passing in the passphrase
        encrypted_key = RSA.RsaKey.export_key(
            key, format='PEM',
            passphrase=passphrase,
            pkcs=1,
            protection=None,
            randfunc=None
        )
        RsaEncrypt.write_key(encrypted_key, pk_file)

    @staticmethod
    def write_key(data, pk_file):
        with open(pk_file, 'wb') as f:
            f.write(data)
            # if data is type(bytes):
            #     f.write(data)
            # else:
            #     key = data.export_key('PEM')
            #     f.write(key)

    @staticmethod
    def decrypt_key(passphrase, pk_file):
        encrypted_key = RsaEncrypt.read_key(pk_file)
        decrypted_key = RSA.import_key(encrypted_key, passphrase)
        RsaEncrypt.write_key(decrypted_key, pk_file)


if __name__ == "__main__":
    password = 'password123'
    file = 'private.key'
    RsaEncrypt.decrypt_key(password, file)


#
#
#
# with open('original_private.key', 'rb') as f:
#     original_key = f.read()
#     print(original_key)
#
# passphrase = 'something'
#
# key = RSA.import_key(original_key, passphrase=None)
# print(key)
# new_key = RSA.RsaKey.export_key(key, format='PEM', passphrase=passphrase, pkcs=1, protection=None, randfunc=None)
#
# with open('original_private.key', 'wb') as f:
#     f.write(new_key)
#
#
# with open('original_private.key', 'rb') as f:
#     encrypted_key = f.read()
#
# wrong_passphrase = 'wrong-password'
# print(encrypted_key)
# decrypted_key = RSA.import_key(encrypted_key, passphrase=passphrase)
# with open('original_private.key', 'wb') as f:
#     decrypted_data = decrypted_key.export_key('PEM')
#     f.write(decrypted_data)
#

# print(decrypted_key)

# secret_code = "password"
# key = RSA.generate(2048)
#
# encrypted_key = key.export_key(passphrase=secret_code, pkcs=8, protection='scryptAndAES128-CBC')
# file_out = open("rsa_key.bin", "wb")
# file_out.write(encrypted_key)
# print(encrypted_key)
# print(key.publickey().export_key())
#
# wrong_code = 'hello'
# encoded_key = open("rsa_key.bin", "rb").read()
# key = RSA.import_key(encrypted_key, passphrase=secret_code)
# print()
# print(key)
# print(key.publickey().export_key())

# print(external_key)
# x = str(RSA.import_key(external_key, passphrase='password').export_key().decode('ascii'))
# print(x)
# key = RSA.import_key('', passphrase=None)
# print(key)
