import binascii
import datetime
from os import urandom

import six
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from user_sync.error import AssertionException


class Certgen:
    country = 'countryName'
    state = 'stateOrProvinceName'
    city = 'localityName'
    organization = 'organizationName'
    common = 'commonName'
    email = 'emailAddress'

    @staticmethod
    def generate(private_key_file, cert_pub_file, subject_fields):
        key = Certgen.create_key()
        certificate = Certgen.create_cert(subject_fields, key)
        Certgen.write_key_to_file(private_key_file, key)
        Certgen.write_cert_to_file(cert_pub_file, certificate)

    @staticmethod
    def get_subject_fields(randomize):
        def values(prompt='', size=6):
            return str(binascii.b2a_hex(urandom(size)).decode()) if randomize else input(prompt)
        return {
            Certgen.country: values('Country Code: ', 1),
            Certgen.state: values('State: '),
            Certgen.city: values('City: '),
            Certgen.organization: values('Organization: '),
            Certgen.common: values('Common Name: '),
            Certgen.email: values('Email: ')
        }

    @staticmethod
    def create_key():
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    @staticmethod
    def create_cert(subject_fields, key):
        try:
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, six.text_type(subject_fields[Certgen.country])),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, six.text_type(subject_fields[Certgen.state])),
                x509.NameAttribute(NameOID.LOCALITY_NAME, six.text_type(subject_fields[Certgen.city])),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, six.text_type(subject_fields[Certgen.organization])),
                x509.NameAttribute(NameOID.COMMON_NAME, six.text_type(subject_fields[Certgen.common])),
                x509.NameAttribute(NameOID.EMAIL_ADDRESS, six.text_type(subject_fields[Certgen.email]))
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
        except ValueError as e:
            raise AssertionException(e)

    @staticmethod
    def write_key_to_file(private_key_file, key):
        with open(private_key_file, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

    @staticmethod
    def write_cert_to_file(cert_pub_file, certificate):
        with open(cert_pub_file, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))
