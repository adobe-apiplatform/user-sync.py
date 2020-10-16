import logging

import pytest

from user_sync.config.sign_sync import SignConfigLoader
from user_sync.config.user_sync import DictConfig
from user_sync.engine.common import AdobeGroup
from user_sync.engine.sign import SignSyncEngine
from user_sync.error import AssertionException


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
    assert group_mappings['Test Group 1']['groups'] == [AdobeGroup.create('Sign Group 1')]

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
    for mapping in group_mappings['Test Group 2']['groups']:
        assert mapping in [AdobeGroup.create('Sign Group 2'), AdobeGroup.create('Sign Group 3')]


# NOTE: tmp_sign_connector_config and tmp_config_files are needed to prevent the ConfigFileLoader
# from complaining that there are no temporary sign connector or ldap connector files
def test_identity_module(sign_config_file, modify_sign_config, tmp_sign_connector_config, tmp_config_files):
    """ensure directory module name is correct"""
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    assert config.get_directory_connector_module_name() == 'user_sync.connector.directory_ldap'

    sign_config_file = modify_sign_config(['identity_source', 'type'], 'okta')
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    assert config.get_directory_connector_module_name() == 'user_sync.connector.directory_okta'


def test_identity_connector_options(sign_config_file):
    """ensure sign connector options are retrieved from Sign config handler"""
    options = {'username': 'ldapuser@example.com', 'password': 'password', 'host': 'ldap://host', 'base_dn': 'DC=example,DC=com', 'search_page_size': 200,
               'require_tls_cert': False, 'all_users_filter': '(&(objectClass=user)(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))',
               'group_filter_format': '(&(|(objectCategory=group)(objectClass=groupOfNames)(objectClass=posixGroup))(cn={group}))',
               'group_member_filter_format': '(memberOf={group_dn})', 'user_email_format': '{mail}'}
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    assert config.get_directory_connector_options('ldap') == options

    with pytest.raises(AssertionException):
        config.get_directory_connector_options('okta')


# NOTE: tmp_sign_connector_config and tmp_config_files are needed to prevent the ConfigFileLoader
# from complaining that there are no temporary sign connector or ldap connector files
def test_target_config_options(sign_config_file, modify_sign_config, tmp_sign_connector_config, tmp_config_files):
    """ensure directory module name is correct"""
    # simple case
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    primary_options, _ = config.get_target_options()
    assert primary_options['host'] == 'api.echosignstage.com'
    assert primary_options['key'] == '[Sign API Key]'
    assert primary_options['admin_email'] == 'user@example.com'

    # complex case
    sign_config_file = modify_sign_config(['sign_orgs'], {'primary': 'connector-sign.yml', 'org2': 'connector-sign.yml'})
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    primary_options, secondary_options = config.get_target_options()
    assert 'org2' in secondary_options
    assert secondary_options['org2']['host'] == 'api.echosignstage.com'
    assert secondary_options['org2']['key'] == '[Sign API Key]'
    assert secondary_options['org2']['admin_email'] == 'user@example.com'

    # invalid case
    sign_config_file = modify_sign_config(['sign_orgs'], {'org1': 'connector-sign.yml'})
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    # 'sign_orgs' must specify a config with the key 'primary'
    with pytest.raises(AssertionException):
        config.get_target_options()


def test_logging_config(sign_config_file):
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    logging_config = config.get_logging_config()
    assert logging_config.get_bool('log_to_file') is True
    assert logging_config.get_string('file_log_directory').endswith('sign_logs')
    assert logging_config.get_string('file_log_name_format') == '{:%Y-%m-%d}-sign.log'
    assert logging_config.get_string('file_log_level') == 'info'
    assert logging_config.get_string('console_log_level') == 'debug'


def test_engine_options(sign_config_file, modify_sign_config, tmp_sign_connector_config, tmp_config_files):
    sign_config_file = modify_sign_config(['user_sync'], {'create_users': False, 'deactivate_users': False, 'sign_only_limit': 1000})
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    options = config.get_engine_options()
    # ensure rule options dict is initialized from default_options
    for k in SignSyncEngine.default_options:
        assert k in options
    # ensure rule options dict is updated with invocation_options
    for k in config.invocation_options:
        assert k in options
    # ensure that we didn't accidentally introduce any new keys in get_engine_options()
    assert not (set(SignSyncEngine.default_options.keys()) | set(config.invocation_options.keys())) - set(options.keys())
    assert options['create_users'] == False
    assert options['sign_only_limit'] == 1000
    