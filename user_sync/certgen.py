import binascii
from datetime import datetime, timedelta
from os import urandom

import click
import six
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from user_sync.error import AssertionException


def generate(private_key_file, cert_pub_file, subject_fields):
    key = create_key()
    certificate = create_cert(subject_fields, key)
    write_key_to_file(private_key_file, key)
    write_cert_to_file(cert_pub_file, certificate)


def get_subject_fields(randomize):
    def values(prompt, default, rnd_size=6):
        if randomize:
            return str(binascii.b2a_hex(urandom(rnd_size)).decode())
        return click.prompt(prompt, default=default)

    exp = datetime.now() + timedelta(days=3653)
    if not randomize:
        exp = click.prompt("Expiration date (mm/dd/yyyy) [{}]".format(exp.strftime('%m/%d/%Y')),
                           type=click.DateTime(formats=("%m/%d/%y", "%m/%d/%Y")),
                           show_default=False,
                           default=exp)

    return {
        'countryName': values('Country Code', 'US', 1),
        'stateOrProvinceName': values('State', 'Your State'),
        'localityName': values('City', 'Your City'),
        'organizationName': values('Organization', 'Company'),
        'commonName': values('Common Name', 'Your Name'),
        'emailAddress': values('Email', 'email@company.com'),
        'expiration': exp
    }


def create_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )


def create_cert(subject_fields, key):
    try:
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, six.text_type(subject_fields['countryName'])),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,
                               six.text_type(subject_fields['stateOrProvinceName'])),
            x509.NameAttribute(NameOID.LOCALITY_NAME, six.text_type(subject_fields['localityName'])),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, six.text_type(subject_fields['organizationName'])),
            x509.NameAttribute(NameOID.COMMON_NAME, six.text_type(subject_fields['commonName'])),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, six.text_type(subject_fields['emailAddress']))
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
            datetime.now() - timedelta(days=1)
        ).not_valid_after(
            subject_fields['expiration']
        ).sign(key, hashes.SHA256(), default_backend())
    except ValueError as e:
        raise AssertionException(e)


def write_key_to_file(private_key_file, key):
    with open(private_key_file, 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))


def write_cert_to_file(cert_pub_file, certificate):
    with open(cert_pub_file, "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))
