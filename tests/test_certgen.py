import re

import pytest

from user_sync.certgen import create_key, get_subject_fields, create_cert, write_cert_to_file, write_key_to_file
from user_sync.error import AssertionException


@pytest.fixture()
def random_subject():
    return get_subject_fields(randomize=True)


@pytest.fixture()
def key():
    return create_key()


def test_get_subject_fields(random_subject):
    assert len(random_subject['countryName']) == 2
    test_keys = set()
    for key in random_subject:
        assert key not in test_keys
        assert re.search('^[a-zA-Z0-9=]{2,}', key)
        test_keys.add(key)


def test_create_key(key):
    assert key.key_size == 2048
    assert key._backend.name == 'openssl'


def test_create_cert(random_subject, key):
    cert = create_cert(random_subject, key)
    cert_dict = {i.oid._name: i.value for i in cert.subject}
    for k, v in cert_dict.items():
        assert random_subject[k] == v
    random_subject['countryName'] = 'usa'
    with pytest.raises(AssertionException):
        create_cert(random_subject, key)


def test_write_key_to_file(test_resources, key):
    write_key_to_file(test_resources['priv_key'], key)
    with open(test_resources['priv_key'], 'r') as f:
        data = f.read()
    opening = '-----BEGIN RSA PRIVATE KEY-----'
    ending = '-----END RSA PRIVATE KEY-----'
    assert opening in data and ending in data


def test_write_cert_to_file(test_resources, random_subject, key):
    public_cert = test_resources['certificate']
    cert = create_cert(random_subject, key)
    write_cert_to_file(public_cert, cert)
    with open(public_cert, 'r') as f:
        data = f.read()
    opening = '-----BEGIN CERTIFICATE-----'
    ending = '-----END CERTIFICATE-----'
    assert opening in data and ending in data
