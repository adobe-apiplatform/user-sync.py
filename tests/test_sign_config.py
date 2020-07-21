import logging
import pytest
import yaml
import os
import shutil
from util import update_dict
from user_sync.config.sign_sync import SignConfigLoader
from user_sync.config.user_sync import DictConfig
from user_sync.engine.common import AdobeGroup


@pytest.fixture
def sign_config_file(fixture_dir):
    return os.path.join(fixture_dir, 'sign-sync-config.yml')


@pytest.fixture
def sign_connector_config(fixture_dir):
    return os.path.join(fixture_dir, 'connector-sign.yml')


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


def test_loader_attributes(sign_config_file):
    """ensure that initial load of Sign config is correct"""
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    assert isinstance(config.logger, logging.Logger)
    assert config.args == args
    assert 'users' in config.invocation_options
    assert 'config_filename' in config.invocation_options
    assert isinstance(config.main_config, DictConfig)


def test_config_structure(sign_config_file):
    """ensure that Sign config test fixture is structured correctly"""
    args = {'config_filename': sign_config_file}
    _ = SignConfigLoader(args)
    # nothing to assert here, if the config object is constructed without exceptions, then the test passes


# NOTE: tmp_sign_connector_config and tmp_config_files are needed to prevent the ConfigFileLoader
# from complaining that there are no temporary sign connector or ldap connector files
def test_invocation_defaults(modify_sign_config, tmp_sign_connector_config, tmp_config_files):
    """ensure that invocation defaults are resolved correctly"""
    sign_config_file = modify_sign_config(['invocation_defaults', 'users'], 'all')
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    assert 'users' in config.invocation_options
    assert config.invocation_options['users'] == ['all']
    args = {'config_filename': sign_config_file, 'users': ['some_option']}
    config = SignConfigLoader(args)
    assert 'users' in config.invocation_options
    assert config.invocation_options['users'] == ['some_option']


# NOTE: tmp_sign_connector_config and tmp_config_files are needed to prevent the ConfigFileLoader
# from complaining that there are no temporary sign connector or ldap connector files
def test_group_config(modify_sign_config, tmp_sign_connector_config, tmp_config_files):
    """ensure that group mappings are loaded correctly"""
    # simple case
    group_config = [{'directory_group': 'Test Group 1', 'sign_group': 'Sign Group 1', 'admin_role': None}]
    sign_config_file = modify_sign_config(['user_management'], group_config)
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    group_mappings = config.get_directory_groups()
    assert 'Test Group 1' in group_mappings
    assert group_mappings['Test Group 1'] == [AdobeGroup.create('Sign Group 1')]

    # complex case
    group_config.append({'directory_group': 'Test Group 2', 'sign_group': 'Sign Group 2', 'admin_role': None})
    group_config.append({'directory_group': 'Test Group 2', 'sign_group': 'Sign Group 3', 'admin_role': None})
    sign_config_file = modify_sign_config(['user_management'], group_config)
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    group_mappings = config.get_directory_groups()
    assert len(group_mappings) == 2
    assert 'Test Group 1' in group_mappings
    assert 'Test Group 2' in group_mappings
    for mapping in group_mappings['Test Group 2']:
        assert mapping in [AdobeGroup.create('Sign Group 2'), AdobeGroup.create('Sign Group 3')]
