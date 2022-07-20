import os
import shutil
from unittest import mock

import pytest

from user_sync.config.user_sync import UMAPIConfigLoader
from user_sync.dcmanager import DirectoryConnectorConfig, DirectoryConnectorManager, DirectoryGroup
from user_sync.error import AssertionException


def connector_dict(id, type, path):
    return {
        'id': id,
        'type': type,
        'path': path,
    }


@pytest.fixture
def multi_config_files(fixture_dir, tmpdir):
    config_files = {
        'src1': 'connector-ldap.yml',
        'src2': 'connector-okta.yml',
        'src3': 'connector-csv.yml',
        'umapi': 'connector-umapi.yml',
        'root_config': 'user-sync-config.yml',
    }

    for k, n in config_files.items():
        shutil.copy(os.path.join(fixture_dir, n), tmpdir)
        config_files[k] = os.path.join(tmpdir, n)
    return config_files


@pytest.fixture()
def dc_manager(multi_config_files, modify_root_config):
    # Skip actually creating the connectors
    DirectoryConnectorManager.build_connector = lambda s, v: v

    # Update root config to use several sources and the correct connector type
    conn_list = [
        connector_dict('src1', 'ldap', multi_config_files['src1']),
        connector_dict('src2', 'okta', multi_config_files['src2']),
        connector_dict('src3', 'csv', multi_config_files['src3'])
    ]

    modify_root_config(['directory_users', 'connectors'], {'multi': conn_list}, merge=False)
    modify_root_config(['invocation_defaults', 'connector'], 'multi', merge=False)

    # Create the config loader
    cl = UMAPIConfigLoader({'config_filename': multi_config_files['root_config'], 'encoding_name': None})

    # Finally, return the DCM
    return DirectoryConnectorManager(cl)


def test_map_list():
    groups = [DirectoryGroup('src1::group name'), DirectoryGroup('second group'), DirectoryGroup('third group')]

    r = DirectoryConnectorManager.list_to_map(groups, 'directory_id')
    assert r['src1'][0] == groups[0]
    assert r[None][0] == groups[1]
    assert r[None][1] == groups[2]


def test_build_directory_groups(dc_manager):
    group_names = ['All Apps', 'src1::Group One']
    dir_groups = dc_manager.build_directory_groups(group_names)

    assert dir_groups[0].directory_id is None
    assert dir_groups[0].common_name == dir_groups[0].fq_name == 'All Apps'

    assert dir_groups[1].directory_id == 'src1'
    assert dir_groups[1].common_name == 'Group One'
    assert dir_groups[1].fq_name == 'src1::Group One'
    assert dir_groups[1].fq_name == 'src1::Group One'

    with pytest.raises(AssertionException):
        dc_manager.build_directory_groups(['bad_id::Group One'])


def test_subsitute_groups_for_user(dc_manager):
    # Test user with an unused group, and a duplicate common name (Group One)
    user = {'groups': ['Group One', 'Group Two']}
    dir_groups = dc_manager.build_directory_groups(['All Apps', 'src1::Group One', 'Group One'])
    dc_manager.substitute_groups_for_user(user, dir_groups)
    assert user['groups'] == ['src1::Group One', 'Group One', 'Group Two']

    # Test an empty user
    user = {'groups': []}
    dir_groups = dc_manager.build_directory_groups(['All Apps', 'src1::Group One', 'Group One'])
    dc_manager.substitute_groups_for_user(user, dir_groups)
    assert user['groups'] == []

    # Test no groups specified
    user = {'groups': ['Group One', 'Group Two']}
    dir_groups = dc_manager.build_directory_groups([])
    dc_manager.substitute_groups_for_user(user, dir_groups)
    assert user['groups'] == ['Group One', 'Group Two']


def test_common_names_for_connector(dc_manager):
    dir_groups = dc_manager.build_directory_groups(['All Apps', 'src1::Group One', 'src2::Group Two', 'Group One'])

    g = dc_manager.common_names_for_connector(dir_groups, 'src1')
    assert g == {'Group One'}
    g = dc_manager.common_names_for_connector(dir_groups, 'src2')
    assert g == {'Group Two'}
    g = dc_manager.common_names_for_connector(dir_groups, None)
    assert g == {'All Apps', 'Group One'}


@mock.patch('user_sync.config.user_sync.UMAPIConfigLoader.get_directory_connector_configs')
def test_build_directory_config_dict(gdcc, dc_manager):
    conn_list = [
        connector_dict('src1', 'ldap', 'path1'),
        connector_dict('src2', 'okta', 'path2'),
        connector_dict('src3', 'csv', 'path3')
    ]

    gdcc.return_value = conn_list
    res = dc_manager.build_directory_config_dict()

    for k, v in res.items():
        assert k in ['src1', 'src2', 'src3']
        assert isinstance(v, DirectoryConnectorConfig)

    conn_list.append(connector_dict('src1', 'ldap2', 'path12'))
    with pytest.raises(AssertionException):
        dc_manager.build_directory_config_dict()

    dc_manager.config_loader.invocation_options['users-file'] = True
    res = dc_manager.build_directory_config_dict()
    assert vars(res['users-file']) == {
        'id': 'users-file',
        'path': None,
        'type': 'csv'
    }
