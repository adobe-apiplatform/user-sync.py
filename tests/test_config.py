import pytest

import user_sync.engine.umapi
import yaml
import shutil
from user_sync.connector.connector_umapi import UmapiConnector
from user_sync.config import ConfigFileLoader, ConfigLoader, DictConfig
from user_sync import flags
from user_sync.config.common import ConfigFileLoader, DictConfig
from user_sync.config.user_sync import UMAPIConfigLoader
from user_sync.connector.directory import DirectoryConnector
from user_sync.connector.directory_ldap import LDAPDirectoryConnector
from user_sync.error import AssertionException

engine_defaults = user_sync.engine.umapi.RuleProcessor.default_options.copy()

def reset_rule_options():
    # Reset the ruleprocessor options since get_engine_options is a destructive method
    # because it changes class variables in memory between tests
    # If options are not reset, subsequent tests may fail
    user_sync.engine.umapi.RuleProcessor.default_options = engine_defaults.copy()


@pytest.fixture()
def cleanup():
    # Failsafe in case of failed test - resets options
    yield
    reset_rule_options()


@pytest.fixture()
def cf_loader():
    return ConfigFileLoader('utf8', UMAPIConfigLoader.ROOT_CONFIG_PATH_KEYS,
                            UMAPIConfigLoader.SUB_CONFIG_PATH_KEYS)


def test_load_root(cf_loader, test_resources):
    """Load root config file and test for presence of root-level keys"""
    root_config = cf_loader.load_root_config(test_resources['umapi_root_config'])
    assert isinstance(root_config, dict)
    assert ('adobe_users' in root_config and 'directory_users' in root_config and
            'logging' in root_config and 'limits' in root_config and
            'invocation_defaults' in root_config)


def test_max_adobe_percentage(cleanup, default_args, modify_root_config, cf_loader):
    root_config_file = modify_root_config(['limits', 'max_adobe_only_users'], "50%")
    config = cf_loader.load_root_config(root_config_file)
    assert ('limits' in config and 'max_adobe_only_users' in config['limits'] and
            config['limits']['max_adobe_only_users'] == "50%")

    reset_rule_options()  # Reset the ruleprocessor
    options = UMAPIConfigLoader(default_args).get_engine_options()
    assert 'max_adobe_only_users' in options and options['max_adobe_only_users'] == '50%'

    modify_root_config(['limits', 'max_adobe_only_users'], "error%")
    reset_rule_options()  # Reset the ruleprocessor
    with pytest.raises(AssertionException):
        UMAPIConfigLoader(default_args).get_engine_options()


def test_additional_groups_config(cleanup, default_args, modify_root_config, cf_loader):
    addl_groups = [
        {
            "source": r"ACL-(.+)",
            "target": r"ACL-Grp-(\1)"},
        {
            "source": r"(.+)-ACL",
            "target": r"ACL-Grp-(\1)"},
    ]
    root_config_file = modify_root_config(['directory_users', 'additional_groups'], addl_groups)
    config = cf_loader.load_root_config(root_config_file)
    assert ('additional_groups' in config['directory_users'] and
            len(config['directory_users']['additional_groups']) == 2)

    reset_rule_options()  # Reset the ruleprocessor
    options = UMAPIConfigLoader(default_args).get_engine_options()
    assert addl_groups[0]['source'] in options['additional_groups'][0]['source'].pattern
    assert addl_groups[1]['source'] in options['additional_groups'][1]['source'].pattern


def test_adobe_users_config(default_args, test_resources, modify_root_config):
    # test default
    config_loader = UMAPIConfigLoader(default_args)
    options = config_loader.load_invocation_options()
    assert 'adobe_users' in options
    assert options['adobe_users'] == ['all']

    # test default invocation
    modify_root_config(['invocation_defaults', 'adobe_users'], "mapped")
    config_loader = UMAPIConfigLoader(default_args)
    options = config_loader.load_invocation_options()
    assert 'adobe_users' in options
    assert options['adobe_users'] == ['mapped']

    # test command line param
    modify_root_config(['invocation_defaults', 'adobe_users'], "all")
    default_args.update({
        'config_filename': test_resources['umapi_root_config'],
        'adobe_users': ['mapped']})
    config_loader = UMAPIConfigLoader(default_args)
    options = config_loader.load_invocation_options()
    assert 'adobe_users' in options
    assert options['adobe_users'] == ['mapped']


def test_directory_users_config(modify_root_config, default_args):
    # test that if connectors is not present or misspelled, an assertion exception is thrown
    modify_root_config(['directory_users'], {'not_connectors': {'ldap': 'connector-ldap.yml'}}, merge=False)
    config_loader = UMAPIConfigLoader(default_args)
    connector_name = 'ldap'
    with pytest.raises(AssertionException):
        config_loader.get_directory_connector_options(connector_name)


def test_extension_load(modify_root_config, monkeypatch, test_resources, default_args, cleanup):
    """Test that extension config is loaded when config option is specified"""
    with monkeypatch.context() as m:
        m.setattr(flags, 'get_flag', lambda *a: True)

        options = UMAPIConfigLoader(default_args).get_engine_options()
        assert 'after_mapping_hook' in options and options['after_mapping_hook'] is None

        modify_root_config(['directory_users', 'extension'], test_resources['extension'])
        options = UMAPIConfigLoader(default_args).get_engine_options()
        assert 'after_mapping_hook' in options and options['after_mapping_hook'] is not None


def test_extension_flag(modify_root_config, monkeypatch, test_resources, default_args, cleanup):
    """Test that extension flag will prevent after-map hook from running"""
    with monkeypatch.context() as m:
        m.setattr(flags, 'get_flag', lambda *a: False)

        modify_root_config(['directory_users', 'extension'], test_resources['extension'])
        options = UMAPIConfigLoader(default_args).get_engine_options()
        assert 'after_mapping_hook' in options and options['after_mapping_hook'] is None


def test_shell_exec_disabled(modify_root_config, default_args):
    """Test that shell exec will raise an error"""
    with pytest.raises(AssertionException):
        modify_root_config(['directory_users', 'connectors', 'ldap'], "$(some command)")
        UMAPIConfigLoader(default_args)


def test_twostep_config(default_args, test_resources, modify_config):
    def load_ldap_config_options(args):
        config_loader = UMAPIConfigLoader(args)
        dc_config_options = config_loader.get_directory_connector_options(LDAPDirectoryConnector.name)
        caller_config = DictConfig('%s configuration' % DirectoryConnector.name, dc_config_options)
        return LDAPDirectoryConnector.get_options(caller_config)

    modify_config('ldap', ['two_steps_lookup'], {})
    # test invalid "two_steps_lookup" config
    with pytest.raises(AssertionException):
        load_ldap_config_options(default_args)

    # test valid "two_steps_lookup" config with "group_member_filter_format" still set
    modify_config('ldap', ['two_steps_lookup', 'group_member_attribute_name'], 'member')
    with pytest.raises(AssertionException):
        load_ldap_config_options(default_args)

    # test valid "two_steps_lookup" setup
    modify_config('ldap', ['two_steps_lookup', 'group_member_attribute_name'], 'member')
    modify_config('ldap', ['group_member_filter_format'], "")
    options = load_ldap_config_options(default_args)
    assert 'two_steps_enabled' in options
    assert 'two_steps_lookup' in options
    assert 'group_member_attribute_name' in options['two_steps_lookup']
    assert options['two_steps_lookup']['group_member_attribute_name'] == 'member'


def test_shell_exec_flag(test_resources, modify_root_config, cli_args, monkeypatch):
    """Test that shell exec flag will raise an error if command is specified to get connector config"""
    with monkeypatch.context() as m:
        m.setattr(flags, 'get_flag', lambda *a: False)
        root_config_file = test_resources['umapi_root_config']

        args = cli_args({'config_filename': root_config_file})
        modify_root_config(['directory_users', 'connectors', 'ldap'], "$(some command)")
        config_loader = ConfigLoader(args)

        directory_connector_module_name = config_loader.get_directory_connector_module_name()
        if directory_connector_module_name is not None:
            directory_connector = DirectoryConnector()
            with pytest.raises(AssertionException):
                config_loader.get_directory_connector_options(directory_connector.name)


def test_uses_business_id_true(tmp_config_files, modify_umapi_config, cli_args, private_key):
    root_config, _, _ = tmp_config_files
    modify_umapi_config(['uses_business_id'], True)
    modify_umapi_config(['enterprise', 'priv_key_path'], private_key)
    args = cli_args({'config_filename': root_config})
    config_loader = ConfigLoader(args)
    connector_options, _ = config_loader.get_umapi_options()
    UmapiConnector.create_conn = False
    umapi_connector = UmapiConnector('.primary', connector_options)
    assert umapi_connector.uses_business_id


def test_uses_business_id_false(tmp_config_files, modify_umapi_config, cli_args, private_key):
    root_config, _, _ = tmp_config_files
    modify_umapi_config(['uses_business_id'], False)
    modify_umapi_config(['enterprise', 'priv_key_path'], private_key)
    args = cli_args({'config_filename': root_config})
    config_loader = ConfigLoader(args)
    connector_options, _ = config_loader.get_umapi_options()
    UmapiConnector.create_conn = False
    umapi_connector = UmapiConnector('.primary', connector_options)
    assert not umapi_connector.uses_business_id


def test_uses_business_id_unspecified(tmp_config_files, modify_umapi_config, cli_args, private_key):
    root_config, _, _ = tmp_config_files
    modify_umapi_config(['enterprise', 'priv_key_path'], private_key)
    args = cli_args({'config_filename': root_config})
    config_loader = ConfigLoader(args)
    connector_options, _ = config_loader.get_umapi_options()
    UmapiConnector.create_conn = False
    umapi_connector = UmapiConnector('.primary', connector_options)
    assert not umapi_connector.uses_business_id
