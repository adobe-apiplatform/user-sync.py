import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class Certgen:
    def __init__(self, credentials, pk_file, cert_file):
        self.credentials = credentials
        self.pk_file = pk_file
        self.cert_file = cert_file
        self.key = self.create_key()

    def create_key(self):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        return key

    def write_key_to_file(self):
        key = self.key
        with open(self.pk_file, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        self.write_certificate_to_file()

    def create_cert(self):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, self.credentials['country']),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.credentials['state']),
            x509.NameAttribute(NameOID.LOCALITY_NAME, self.credentials['city']),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.credentials['organization']),
            x509.NameAttribute(NameOID.COMMON_NAME, self.credentials['common']),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, self.credentials['email'])
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=10)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        ).sign(self.key, hashes.SHA256(), default_backend())
        return cert

    def write_certificate_to_file(self):
        cert = self.create_cert()
        with open(self.cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
