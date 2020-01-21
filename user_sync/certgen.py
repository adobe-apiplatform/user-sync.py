import datetime
import random
import string

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class Certgen:
    def generate(self, private_key_file, cert_pub_file, credentials):
        key = self.create_key()
        self.write_key_to_file(private_key_file, key)
        certificate = self.create_cert(credentials, key)
        self.write_cert_to_file(cert_pub_file, certificate)

    def random_generator(self, size=15, chars=string.ascii_letters):
        return ''.join(random.choice(chars) for x in range(size))

    def get_credentials(self, randomize):
        if randomize:
            country = self.random_generator(2)
            state = self.random_generator()
            city = self.random_generator()
            organization = self.random_generator()
            common = self.random_generator()
            email = self.random_generator()
        else:
            country = input('Country Code: ')
            state = input('State or Province: ')
            city = input('City: ')
            organization = input('Organization: ')
            common = input('Common Name: ')
            email = input('Email: ')
        return {
            'country': country,
            'state': state,
            'city': city,
            'organization': organization,
            'common': common,
            'email': email
        }

    def create_key(self):
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    def write_key_to_file(self, private_key_file, key):
        with open(private_key_file, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

    def create_cert(self, credentials, key):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, credentials['country']),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, credentials['state']),
            x509.NameAttribute(NameOID.LOCALITY_NAME, credentials['city']),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, credentials['organization']),
            x509.NameAttribute(NameOID.COMMON_NAME, credentials['common']),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, credentials['email'])
        ])

        return x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        ).sign(key, hashes.SHA256(), default_backend())

    def write_cert_to_file(self, cert_pub_file, certificate):
        with open(cert_pub_file, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

# Handle some validation for the fields (so special characters and such)
