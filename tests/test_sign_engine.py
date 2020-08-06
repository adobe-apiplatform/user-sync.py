import pytest
import six
import yaml

from tests.util import update_dict
from user_sync.config.sign_sync import SignConfigLoader
from user_sync.connector.directory import DirectoryConnector
from user_sync.engine.sign import SignSyncEngine


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
def example_user():
    return {
        'user@example.com':
            {'type': 'federatedID',
             'username': 'user@example.com',
             'domain': 'example.com',
             'email': 'user@example.com',
             'firstname': 'Example',
             'lastname': 'User',
             'groups': set(),
             'country': 'US'}
    }


def test_run_sign_engine(modify_root_config, sign_config_file, example_user):
    root_config_file = modify_root_config(['post_sync', 'modules'], 'sign_sync')
    root_config_file = modify_root_config(['post_sync', 'connectors'], sign_config_file)
    args = {'config_filename': sign_config_file}
    args['entitlement_groups'] = 'signgroup'
    args['sign_orgs'] = []
    engine = SignSyncEngine(args)
    assert isinstance(engine, SignSyncEngine)
    dc = DirectoryConnector

    def dir_user_replacement(groups=['testgroup'], extended_attributes=[], all_users=False):
        return six.itervalues(example_user)

    dc.load_users_and_groups = dir_user_replacement
    # def update_sign_replacement()
    engine.run(['testgroup'], dc)
    assert 1 == 1
    #DO TOMORROW MORNING
    # get return value from load users and groups. replace reference to update with assert dir users not none, then do run and it should call that at the end
