import pytest

from user_sync.connector.directory import DirectoryConnector
from user_sync.error import AssertionException


@pytest.fixture
def get_implementation():
    dc_mod_name = "user_sync.connector.directory_ldap"
    return __import__(dc_mod_name, fromlist=[''])


def test_required_functions(get_implementation):
    base_impl = get_implementation
    del base_impl.connector_metadata
    pytest.raises(AssertionException, DirectoryConnector, base_impl)

    base_impl = get_implementation
    del base_impl.connector_initialize
    pytest.raises(AssertionException, DirectoryConnector, base_impl)
