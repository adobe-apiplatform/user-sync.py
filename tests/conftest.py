import os

import pytest
from user_sync.config.user_sync import UserSyncConfigLoader

import shutil


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
        for k in UserSyncConfigLoader.invocation_defaults:
            args_out[k] = None
        for k, v in args_in.items():
            args_out[k] = v
        return args_out

    return _cli_args


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