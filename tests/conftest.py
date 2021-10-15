import os
import shutil

import pytest
import yaml

from util import make_dict, merge_dict
from user_sync import config
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
        for k in config.ConfigLoader.invocation_defaults:
            args_out[k] = None
        for k, v in args_in.items():
            args_out[k] = v
        return args_out

    return _cli_args


@pytest.fixture
def private_key(fixture_dir, tmpdir):
    shutil.copy(os.path.join(fixture_dir, 'test_private.key'), tmpdir)
    return os.path.join(tmpdir, 'test_private.key')


@pytest.fixture
def public_cert(fixture_dir, tmpdir):
    shutil.copy(os.path.join(fixture_dir, 'test_cert.crt'), tmpdir)
    return os.path.join(tmpdir, 'test_cert.crt')

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

@pytest.fixture
def config_files(fixture_dir, tmpdir):
    config_files = {
        'ldap': 'connector-ldap.yml',
        'umapi': 'connector-umapi.yml',
        'root_config': 'user-sync-config.yml',
        'extension': 'extension-config.yml',
    }

    for k, n in config_files.items():
        shutil.copy(os.path.join(fixture_dir, n), tmpdir.dirname)
        config_files[k] = os.path.join(tmpdir.dirname, n)
    return config_files


@pytest.fixture
def modify_config(config_files):
    def _modify_config(name, key, value, replace=False):
        path = config_files[name]
        conf = yaml.safe_load(open(path))
        if replace:
            conf.update(make_dict(key, value))
        else:
            merge_dict(conf, make_dict(key, value))
        yaml.dump(conf, open(path, 'w'))
        return path

    return _modify_config


# A shortcut for root
@pytest.fixture
def modify_root_config(modify_config):
    def _modify_root_config(key, value, replace=False):
        return modify_config('root_config', key, value, replace)

    return _modify_root_config


# A shortcut for loading the config file
@pytest.fixture
def default_args(cli_args, config_files):
    return cli_args({'config_filename': config_files['root_config']})
