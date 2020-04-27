import pytest

from user_sync.config import ConfigFileLoader, DictConfig
from user_sync.connector.umapi_util import has_credential
from user_sync.error import AssertionException


def test_has_credential(umapi_config_file, private_key):
    umapi_config = ConfigFileLoader.load_from_yaml(umapi_config_file, {})
    umapi_dict_config = DictConfig('testscope', umapi_config)
    # with no changes the default umapi config, there will be no key for priv_key_data,
    # so has_credential should return none (it is only called for priv_key_data)
    assert has_credential('priv_key_data', umapi_dict_config) is None
    # if there is a value for priv_key_data then has_credential simply returns the name passed in
    umapi_config['priv_key_data'] = 'keydata'
    assert has_credential('priv_key_data', umapi_dict_config) == 'priv_key_data'
    # if there is also a setting for 'secure_priv_key_data_key' it should throw an AssertionException
    umapi_config['secure_priv_key_data_key'] = 'secure key data'
    with pytest.raises(AssertionException):
        data = has_credential('priv_key_data', umapi_dict_config)
    umapi_config['priv_key_data'] = None
    # if there is only the secure key format then has_credential returns the secure key
    assert has_credential('priv_key_data', umapi_dict_config) == 'secure_priv_key_data_key'



