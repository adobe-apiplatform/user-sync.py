import pytest
from user_sync.error import AssertionException
from user_sync.identity_type import parse_identity_type


def test_parse_valid():
    assert parse_identity_type('federatedID') == 'federatedID'
    assert parse_identity_type('adobeID') == 'adobeID'
    assert parse_identity_type('enterpriseID') == 'enterpriseID'
    assert parse_identity_type('EnterpriseID') == 'enterpriseID'
    assert parse_identity_type('   EnterpriseID   ') == 'enterpriseID'
    assert parse_identity_type('FEDERATEDid') == 'federatedID'


def test_parse_invalid():
    with pytest.raises(AssertionException):
        parse_identity_type('federated_id')

    with pytest.raises(AssertionException) as exc_info:
        parse_identity_type('federated_id', 'Test: %s')
    assert exc_info.value.args[0] == 'Test: Unrecognized identity type: "federated_id"'
