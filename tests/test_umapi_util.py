import pytest

from user_sync.config import ConfigFileLoader, DictConfig
from user_sync.connector.umapi_util import make_auth_dict
from user_sync.error import AssertionException
import user_sync.connector.helper
from user_sync.credentials import CredentialConfig


def test_make_auth_dict(umapi_config_file, private_key):
    umapi_config = ConfigFileLoader.load_from_yaml(umapi_config_file, {})
    umapi_config['enterprise']['priv_key_path'] = private_key
    # note that the private_key fixture is actually just the absolute path to test_private.key in the fixture dir
    umapi_dict_config = DictConfig('enterprise', umapi_config['enterprise'])
    org_id_from_file = umapi_config['enterprise']['org_id']
    tech_acct_from_file = umapi_config['enterprise']['tech_acct']
    api_key_from_file = umapi_config['enterprise']['api_key']
    client_secret_from_file = umapi_config['enterprise']['client_secret']
    logger = user_sync.connector.helper.create_logger({})
    name = 'umapi'
    auth_dict = make_auth_dict(name, umapi_dict_config, org_id_from_file, tech_acct_from_file, logger)
    assert auth_dict['org_id'] == org_id_from_file
    assert auth_dict['tech_acct_id'] == tech_acct_from_file
    assert auth_dict['api_key'] == api_key_from_file
    assert auth_dict['client_secret'] == client_secret_from_file
    with open(private_key) as f:
        key_data_from_file = f.read()
    assert auth_dict['private_key_data'] == key_data_from_file
    # set priv_key_path to none and use priv_key_data instead
    umapi_config['enterprise']['priv_key_path'] = None
    umapi_config['enterprise']['priv_key_data'] = key_data_from_file
    # make sure that auth dict will still return the key data correctly
    auth_dict_key_data = make_auth_dict(name, umapi_dict_config, org_id_from_file, tech_acct_from_file, logger)
    assert auth_dict_key_data['private_key_data'] == key_data_from_file





