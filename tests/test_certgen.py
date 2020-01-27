import os
import re
import shutil
import pytest
from io import StringIO

from user_sync.certgen import Certgen
from user_sync.error import AssertionException


def test_values():
    randomize = True
    values = Certgen.values(randomize)
    regex = re.compile('^[a-zA-Z]{15}$', re.I)
    assert regex.match(values)


def test_get_subject_fields():
    randomize = True
    subject = Certgen.get_subject_fields(randomize)
    regex = re.compile('^[a-zA-Z]{2}$', re.I)
    assert regex.match(subject['country'])
    regex = re.compile('^[a-zA-Z]{15}$', re.I)
    for key in subject:
        if key != 'country':
            assert regex.match(subject[key])


def test_create_key():
    key = Certgen.create_key()
    assert key.key_size == 2048
    assert key._backend.name == 'openssl'


def test_create_cert():
    subject_fields = {
        'country': 'us',
        'state': 'subject',
        'city': 'subject',
        'organization': 'subject',
        'common': 'subject',
        'email': 'subject'
    }
    key = Certgen.create_key()
    data = Certgen.create_cert(subject_fields, key)
    cert_dict = {i.oid._name: i.value for i in data.subject}
    expected_dict = {
        'countryName': 'us',
        'stateOrProvinceName': 'subject',
        'localityName': 'subject',
        'organizationName': 'subject',
        'commonName': 'subject',
        'emailAddress': 'subject'
    }
    assert cert_dict == expected_dict
    subject_fields = {
        'country': 'usa',
        'state': 'subject',
        'city': 'subject',
        'organization': 'subject',
        'common': 'subject',
        'email': 'subject'
    }
    key = Certgen.create_key()
    data = Certgen.create_cert(subject_fields, key)



def test_write_key_to_file(private_key):
    key = Certgen.create_key()
    Certgen.write_key_to_file(private_key, key)
    with open(private_key, 'rb') as f:
        data = f.read()
    opening = '-----BEGIN RSA PRIVATE KEY-----'.encode()
    print(os.path.abspath(private_key))
    assert opening in data


def test_write_cert_to_file(public_cert):
    key = Certgen.create_key()
    subject = {
        'country': 'us',
        'state': 'subject',
        'city': 'subject',
        'organization': 'subject',
        'common': 'subject',
        'email': 'subject'
    }
    cert = Certgen.create_cert(subject, key)
    Certgen.write_cert_to_file(public_cert, cert)
    with open(public_cert, 'rb') as f:
        data = f.read()
    opening = '-----BEGIN CERTIFICATE-----'.encode()
    ending = '-----END CERTIFICATE-----'.encode()
    print()
    print(data)
    assert opening in data and ending in data


