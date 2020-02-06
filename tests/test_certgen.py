import re
import pytest
import six

from user_sync.certgen import Certgen
from user_sync.error import AssertionException


@pytest.fixture()
def random_subject():
    return Certgen.get_subject_fields(randomize=True)


@pytest.fixture()
def key():
    return Certgen.create_key()


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
    days = 3650
    cert = Certgen.create_cert(random_subject, key, days)
    cert_dict = {i.oid._name: i.value for i in cert.subject}
    for k, v in six.iteritems(cert_dict):
        assert random_subject[k] == v
    random_subject['countryName'] = 'usa'
    with pytest.raises(AssertionException):
        Certgen.create_cert(random_subject, key, days)


def test_write_key_to_file(private_key, key):
    Certgen.write_key_to_file(private_key, key)
    with open(private_key, 'r') as f:
        data = f.read()
    opening = '-----BEGIN RSA PRIVATE KEY-----'
    ending = '-----END RSA PRIVATE KEY-----'
    assert opening in data and ending in data


def test_write_cert_to_file(public_cert, random_subject, key):
    days = 3650
    cert = Certgen.create_cert(random_subject, key, days)
    Certgen.write_cert_to_file(public_cert, cert)
    with open(public_cert, 'r') as f:
        data = f.read()
    opening = '-----BEGIN CERTIFICATE-----'
    ending = '-----END CERTIFICATE-----'
    assert opening in data and ending in data
