import os
import pytest
import yaml
import shutil
from mock import MagicMock
from util import update_dict
from user_sync.config import ConfigFileLoader, ConfigLoader, DictConfig
from user_sync import app
from user_sync.error import AssertionException


def load_ldap_config_options(args):
    from user_sync.connector.directory import DirectoryConnector
    from user_sync.connector.directory_ldap import LDAPDirectoryConnector

    config_loader = ConfigLoader(args)
    dc_mod_name = config_loader.get_directory_connector_module_name()
    dc_mod = __import__(dc_mod_name, fromlist=[''])
    dc = DirectoryConnector(dc_mod)
    dc_config_options = config_loader.get_directory_connector_options(dc.name)
    caller_config = DictConfig('%s configuration' % dc.name, dc_config_options)
    return LDAPDirectoryConnector.get_options(caller_config)


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
def tmp_config_files(root_config_file, ldap_config_file, umapi_config_file, extension_config_file, tmpdir):
    tmpfiles = []
    for fname in [root_config_file, ldap_config_file, umapi_config_file, extension_config_file]:
        basename = os.path.split(fname)[-1]
        tmpfile = os.path.join(str(tmpdir), basename)
        shutil.copy(fname, tmpfile)
        tmpfiles.append(tmpfile)
    return tuple(tmpfiles)


@pytest.fixture
def modify_root_config(tmp_config_files):
    (root_config_file, _, _, _) = tmp_config_files

    def _modify_root_config(keys, val):
        conf = yaml.safe_load(open(root_config_file))
        conf = update_dict(conf, keys, val)
        yaml.dump(conf, open(root_config_file, 'w'))

        return root_config_file

    return _modify_root_config


@pytest.fixture
def modify_root_extension_config(tmp_config_files):
    (_, _, _, extension_config_file) = tmp_config_files

    def _modify_root_extension_config(keys, val):
        conf = yaml.safe_load(open(extension_config_file))
        conf = update_dict(conf, keys, val)
        yaml.dump(conf, open(extension_config_file, 'w'))

        return extension_config_file

    return _modify_root_extension_config


@pytest.fixture
def modify_ldap_config(tmp_config_files):
    (_, ldap_config_file, _,) = tmp_config_files

    def _modify_ldap_config(keys, val):
        conf = yaml.safe_load(open(ldap_config_file))
        conf = update_dict(conf, keys, val)
        yaml.dump(conf, open(ldap_config_file, 'w'))

        return ldap_config_file

    return _modify_ldap_config


def test_load_root(root_config_file):
    """Load root config file and test for presence of root-level keys"""
    config = ConfigFileLoader.load_root_config(root_config_file)
    assert isinstance(config, dict)
    assert ('adobe_users' in config and 'directory_users' in config and
            'logging' in config and 'limits' in config and
            'invocation_defaults' in config)


def test_max_adobe_percentage(modify_root_config, cli_args):
    root_config_file = modify_root_config(['limits', 'max_adobe_only_users'], "50%")
    config = ConfigFileLoader.load_root_config(root_config_file)
    assert ('limits' in config and 'max_adobe_only_users' in config['limits'] and
            config['limits']['max_adobe_only_users'] == "50%")

    args = cli_args({'config_filename': root_config_file})
    options = ConfigLoader(args).get_rule_options()
    assert 'max_adobe_only_users' in options and options['max_adobe_only_users'] == '50%'

    modify_root_config(['limits', 'max_adobe_only_users'], "error%")
    with pytest.raises(AssertionException):
        ConfigLoader(args).get_rule_options()


def test_additional_groups_config(modify_root_config, cli_args):
    addl_groups = [
        {"source": r"ACL-(.+)", "target": r"ACL-Grp-(\1)"},
        {"source": r"(.+)-ACL", "target": r"ACL-Grp-(\1)"},
    ]
    root_config_file = modify_root_config(['directory_users', 'additional_groups'], addl_groups)
    config = ConfigFileLoader.load_root_config(root_config_file)
    assert ('additional_groups' in config['directory_users'] and
            len(config['directory_users']['additional_groups']) == 2)

    args = cli_args({'config_filename': root_config_file})
    options = ConfigLoader(args).get_rule_options()
    assert addl_groups[0]['source'] in options['additional_groups'][0]['source'].pattern
    assert addl_groups[1]['source'] in options['additional_groups'][1]['source'].pattern


def test_twostep_config(tmp_config_files, modify_ldap_config, cli_args):
    (root_config_file, ldap_config_file, _) = tmp_config_files
    modify_ldap_config(['two_steps_lookup'], {})

    args = cli_args({'config_filename': root_config_file})

    # test invalid "two_steps_lookup" config
    with pytest.raises(AssertionException):
        load_ldap_config_options(args)

    # test valid "two_steps_lookup" config with "group_member_filter_format" still set
    modify_ldap_config(['two_steps_lookup', 'group_member_attribute_name'], 'member')
    with pytest.raises(AssertionException):
        load_ldap_config_options(args)

    # test valid "two_steps_lookup" setup
    modify_ldap_config(['two_steps_lookup', 'group_member_attribute_name'], 'member')
    modify_ldap_config(['group_member_filter_format'], "")
    options = load_ldap_config_options(args)
    assert 'two_steps_enabled' in options
    assert 'two_steps_lookup' in options
    assert 'group_member_attribute_name' in options['two_steps_lookup']
    assert options['two_steps_lookup']['group_member_attribute_name'] == 'member'


def test_adobe_users_config(tmp_config_files, modify_root_config, cli_args):
    (root_config_file, _, _) = tmp_config_files
    args = cli_args({'config_filename': root_config_file})

    # test default
    config_loader = ConfigLoader(args)
    options = config_loader.load_invocation_options()
    assert 'adobe_users' in options
    assert options['adobe_users'] == ['all']

    # test default invocation
    modify_root_config(['invocation_defaults', 'adobe_users'], "mapped")
    config_loader = ConfigLoader(args)
    options = config_loader.load_invocation_options()
    assert 'adobe_users' in options
    assert options['adobe_users'] == ['mapped']

    # test command line param
    modify_root_config(['invocation_defaults', 'adobe_users'], "all")
    args = cli_args({'config_filename': root_config_file, 'adobe_users': ['mapped']})
    config_loader = ConfigLoader(args)
    options = config_loader.load_invocation_options()
    assert 'adobe_users' in options
    assert options['adobe_users'] == ['mapped']


def test_get_directory_connector_options(tmp_config_files, modify_root_config, cli_args):
    (root_config_file, ldap_config_file, _) = tmp_config_files
    args = cli_args({'config_filename': root_config_file})
    config_loader = ConfigLoader(args)
    with open(ldap_config_file, 'r') as rc:
        x = yaml.safe_load(rc)
    # test when 'ldap' is the connector_name

    assert config_loader.get_directory_connector_options('ldap') == x

    # test when 'csv' is the connector_name

    assert config_loader.get_directory_connector_options('csv') == {}

    # test when the connector_name is not 'csv' and also neither in the connector_config value

    pytest.raises(AssertionException, config_loader.get_directory_connector_options, connector_name='example')


def test_get_dict_from_sources(tmp_config_files, modify_root_config, cli_args):
    (root_config_file, ldap_config_file, _) = tmp_config_files
    args = cli_args({'config_filename': root_config_file})
    config_loader = ConfigLoader(args)
    with open(root_config_file, 'r') as rc:
        x = yaml.safe_load(rc)

    with open(ldap_config_file, 'r') as rc:
        x.update(yaml.safe_load(rc))

    # Test when  the list of sources is empty

    assert config_loader.get_dict_from_sources([]) == {}

    # Test when the list of sources is not empty

    y = config_loader.get_dict_from_sources([root_config_file, ldap_config_file])
    assert x == y


def test_combine_dicts(tmp_config_files, modify_root_config, cli_args):
    (root_config_file, ldap_config_file, _) = tmp_config_files
    args = cli_args({'config_filename': root_config_file})
    config_loader = ConfigLoader(args)
    # Create a dummy dict

    dict1 = {'server': {'host': 'dummy1-stage.adobe.io', 'ims_host': 'ims-na1-stg1.adobelogin.com', 'saba': 'saba'},
             'enterprise': {'org_id': 'D28927675A9581A20A49412A@AdobeOrg',
                            'api_key': 'b348211181c74a8f84dba226cba72cac',
                            'client_secret': '51802159-c3f2-4549-8ac1-0d607ee558c3',
                            'tech_acct': '57C7738C5D67F8420A494216@techacct.adobe.com',
                            'priv_key_path': 'C:\\Program Files\\Adobe\\Adobe User Sync ToolSaba\\private.key'}}
    dict2 = {'server': {'host': 'dummy2-stage.adobe.io', 'ims_host': 'ims-na1-stg1.adobelogin.com'},
             'enterprise': {'mike': 'mike', 'org_id': 'D28927675A9581A20A49412A@AdobeOrg',
                            'api_key': 'b348211181c74a8f84dba226cba72cac',
                            'client_secret': '51802159-c3f2-4549-8ac1-0d607ee558c3',
                            'tech_acct': '57C7738C5D67F8420A494216@techacct.adobe.com',
                            'priv_key_path': 'C:\\Program Files\\Adobe\\Adobe User Sync ToolSaba\\private.key'}}

    result = config_loader.combine_dicts([dict1, dict2])

    dict2['server']['saba'] = 'saba'
    assert dict2 == result


def test_get_directory_extension_option(tmp_config_files, modify_root_config, cli_args, modify_root_extension_config):
    (root_config_file, _, _, extension_config_file) = tmp_config_files

    # adding the extension file  location in the user_sync_config
    modify_root_config(['directory_users', 'extension'], 'extension-config.yml')
    # needed if we want to modify the extension file
    #modify_root_extension_config(['directory_users', 'extension'], 'extension-config.yml')
    # get the config loader object
    args = cli_args({'config_filename': root_config_file})
    config_loader = ConfigLoader(args)

    modify_root_extension_config(['after_mapping_hook'], None)
    with pytest.raises(AssertionError):
        config_loader.get_directory_extension_options()

    modify_root_config(['directory_users', 'extension'], '')
    # resetting the config loader
    args = cli_args({'config_filename': root_config_file})
    config_loader = ConfigLoader(args)
    assert config_loader.get_directory_extension_options() == {}

    print()
