import os
import shutil

import pytest
import yaml

import shutil

from user_sync.config.user_sync import UMAPIConfigLoader

from .util import update_dict


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


@pytest.fixture
def private_key(fixture_dir, tmpdir):
    shutil.copy(os.path.join(fixture_dir, 'test_private.key'), tmpdir.dirname)
    return os.path.join(tmpdir.dirname, 'test_private.key')


@pytest.fixture
def public_cert(fixture_dir, tmpdir):
    shutil.copy(os.path.join(fixture_dir, 'test_cert.crt'), tmpdir.dirname)
    return os.path.join(tmpdir.dirname, 'test_cert.crt')


@pytest.fixture
def root_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'user-sync-config.yml')


@pytest.fixture
def ldap_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'connector-ldap.yml')


@pytest.fixture
def umapi_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'connector-umapi.yml')


@pytest.fixture
def extension_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'extension-config.yml')


@pytest.fixture
def tmp_config_files(root_config_file, ldap_config_file, umapi_config_file, tmpdir):
    tmpfiles = []
    for fname in [root_config_file, ldap_config_file, umapi_config_file]:
        basename = os.path.split(fname)[-1]
        tmpfile = os.path.join(str(tmpdir), basename)
        shutil.copy(fname, tmpfile)
        tmpfiles.append(tmpfile)
    return tuple(tmpfiles)


@pytest.fixture
def modify_root_config(tmp_config_files):
    (root_config_file, _, _) = tmp_config_files

    def _modify_root_config(keys, val):
        conf = yaml.safe_load(open(root_config_file))
        conf = update_dict(conf, keys, val)
        yaml.dump(conf, open(root_config_file, 'w'))

        return root_config_file

    return _modify_root_config


@pytest.fixture
def modify_ldap_config(tmp_config_files):
    (_, ldap_config_file, _) = tmp_config_files

    def _modify_ldap_config(keys, val):
        conf = yaml.safe_load(open(ldap_config_file))
        conf = update_dict(conf, keys, val)
        yaml.dump(conf, open(ldap_config_file, 'w'))

        return ldap_config_file

    return _modify_ldap_config


@pytest.fixture
def sign_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'sign-sync-config.yml')


@pytest.fixture
def sign_connector_config(fixture_dir):
    return os.path.join(fixture_dir, 'connector-sign.yml')


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
def tmp_sign_config_file(sign_config_file, tmpdir):
    basename = os.path.split(sign_config_file)[-1]
    tmpfile = os.path.join(str(tmpdir), basename)
    shutil.copy(sign_config_file, tmpfile)
    return tmpfile


@pytest.fixture
def tmp_sign_connector_config(sign_connector_config, tmpdir):
    basename = os.path.split(sign_connector_config)[-1]
    tmpfile = os.path.join(str(tmpdir), basename)
    shutil.copy(sign_connector_config, tmpfile)
    return tmpfile


@pytest.fixture
def modify_sign_config(tmp_sign_config_file):
    def _modify_sign_config(keys, val):
        conf = yaml.safe_load(open(tmp_sign_config_file))
        conf = update_dict(conf, keys, val)
        yaml.dump(conf, open(tmp_sign_config_file, 'w'))

        return tmp_sign_config_file
    return _modify_sign_config
