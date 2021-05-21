import os
import shutil

import pytest
import yaml

from user_sync.config.user_sync import UMAPIConfigLoader
from .util import merge_dict, make_dict


@pytest.fixture
def fixture_dir():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 'fixture'))


@pytest.fixture
def cli_args():
    def _cli_args(args_in):
        """
        :param dict args:
        :return dict:
        """

        args_out = {}
        for k in UMAPIConfigLoader.invocation_defaults:
            args_out[k] = None
        for k, v in args_in.items():
            args_out[k] = v
        return args_out

    return _cli_args


@pytest.fixture
def test_resources(fixture_dir, tmpdir):
    resources = {
        'ldap': 'connector-ldap.yml',
        'umapi': 'connector-umapi.yml',
        'sign': 'connector-sign.yml',
        'umapi_root_config': 'user-sync-config.yml',
        'sign_root_config': 'sign-sync-config.yml',
        'extension': 'extension-config.yml',
        'certificate': 'test_cert.crt',
        'priv_key': 'test_private.key',
        'priv_key_enc': 'encrypted.key'

    }

    for k, n in resources.items():
        shutil.copy(os.path.join(fixture_dir, n), tmpdir.dirname)
        resources[k] = os.path.join(tmpdir.dirname, n)
    return resources


@pytest.fixture
def modify_config(test_resources):
    def _modify_config(name, key, value, merge=True):
        path = test_resources[name]
        conf = yaml.safe_load(open(path))
        d = make_dict(key, value)
        if not merge:
            conf.update(d)
        else:
            merge_dict(conf, make_dict(key, value))
        yaml.dump(conf, open(path, 'w'))
        return path

    return _modify_config


# A shortcut for root since it is used a lot
@pytest.fixture
def modify_root_config(modify_config):
    def _modify_root_config(key, value, merge=True):
        return modify_config('umapi_root_config', key, value, merge)

    return _modify_root_config


# A shortcut for loading the config file
@pytest.fixture
def default_args(cli_args, test_resources):
    return cli_args({'config_filename': test_resources['umapi_root_config']})

# A shortcut for loading the config file
@pytest.fixture
def default_sign_args(cli_args, test_resources):
    return cli_args({'config_filename': test_resources['sign_root_config']})

@pytest.fixture
def resource_file():
    """
    Create an empty resource file
    :return:
    """

    def _resource_file(dirname, filename):
        filepath = os.path.join(dirname, filename)
        open(filepath, 'a').close()
        return filepath

    return _resource_file

@pytest.fixture
def example_user():
    return {
        'type': 'federatedID',
        'username': 'user@example.com',
        'domain': 'example.com',
        'email': 'user@example.com',
        'firstname': 'Example',
        'lastname': 'User',
        'groups': set(),
        'country': 'US',
    }