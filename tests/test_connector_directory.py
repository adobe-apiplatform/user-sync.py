import os
import pytest

@pytest.fixture
def get_implementation(object):
    # from user_sync.connector.directory import DirectoryConnector
    #
    # config_loader = ConfigLoader(args)
    # dc_mod_name = config_loader.get_directory_connector_module_name()
    # dc_mod = __import__(dc_mod_name, fromlist=[''])
    # dc = DirectoryConnector(dc_mod)

    # something like this...???

    pass

def test_required_functions():

    # need to give this some sort of implementation (perhaps as a fixture)
    # validate that exception is thrown if the implementation is missing the required functions
    # look at debug and test_config.py:

    pass

def test_initialize():

    # use mock implementation above to call connector_initialize
    # assert self.state set to properly initialized instance of connector

    pass

def test_load_users_and_groups():

    # not sure this needs a real test, since all it's doing is acting as a pass through
    # maybe we can validate the methods are being called correctly via connector_load_users_and_groups
    # since they are being executed via self.state 

    pass
