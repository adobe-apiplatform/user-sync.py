import os
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



def test_initialize():



    print()

    # use mock implementation above to call connector_initialize
    # assert self.state set to properly initialized instance of connector

    pass

def test_load_users_and_groups():

    # not sure this needs a real test, since all it's doing is acting as a pass through
    # maybe we can validate the methods are being called correctly via connector_load_users_and_groups
    # since they are being executed via self.state 

    pass
