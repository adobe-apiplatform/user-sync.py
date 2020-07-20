import logging
import pytest
import yaml
from util import update_dict
from user_sync.config.sign_sync import SignConfigLoader
from user_sync.config.user_sync import DictConfig


@pytest.fixture
def modify_sign_config(sign_config_file):
    def _modify_sign_config(keys, val):
        conf = yaml.safe_load(open(sign_config_file))
        conf = update_dict(conf, keys, val)
        yaml.dump(conf, open(sign_config_file, 'w'))

        return sign_config_file
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
    config = SignConfigLoader(args)
    assert 'sign_orgs' in config.main_config
    assert 'primary' in config.main_config.get_dict('sign_orgs')
    assert 'identity_source' in config.main_config
    assert 'type' in config.main_config.get_dict('identity_source')
    assert 'connector' in config.main_config.get_dict('identity_source')
    assert 'user_sync' in config.main_config
    assert 'create_users' in config.main_config.get_dict('user_sync')
    assert 'sign_only_limit' in config.main_config.get_dict('user_sync')
    assert 'user_management' in config.main_config
    assert 'logging' in config.main_config
    assert 'log_to_file' in config.main_config.get_dict('logging')
    assert 'file_log_directory' in config.main_config.get_dict('logging')
    assert 'file_log_name_format' in config.main_config.get_dict('logging')
    assert 'file_log_level' in config.main_config.get_dict('logging')
    assert 'console_log_level' in config.main_config.get_dict('logging')
    assert 'invocation_defaults' in config.main_config
    assert 'users' in config.main_config.get_dict('invocation_defaults')


def test_invocation_defaults(modify_sign_config):
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
