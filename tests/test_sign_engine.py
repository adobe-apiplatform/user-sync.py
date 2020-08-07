import pytest
import six
import yaml

from tests.util import update_dict
from user_sync.config.sign_sync import SignConfigLoader
from user_sync.connector.connector_sign import SignConnector
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


@pytest.fixture
def example_engine(modify_root_config, sign_config_file):
    root_config_file = modify_root_config(['post_sync', 'modules'], 'sign_sync')
    root_config_file = modify_root_config(['post_sync', 'connectors'], sign_config_file)
    args = {'config_filename': sign_config_file}
    args['entitlement_groups'] = 'signgroup'
    args['sign_orgs'] = []
    return SignSyncEngine(args)


def test_load_users_and_groups(example_engine, example_user):
    dc = DirectoryConnector

    def dir_user_replacement(groups, extended_attributes, all_users):
        return six.itervalues(example_user)

    # replace the call to load directory groups and users with the example user dict. this dict will then be modified
    # by other methods in the engine/sign.py which are almost identical to the same methods in engine/umapi.py right now
    # these methods should be altered for sign-specific usage - for example, there's no need to specify an identity
    # type for sign-syncing purposes, but it has been left in there so that the code can run
    dc.load_users_and_groups = dir_user_replacement
    directory_users = example_engine.read_desired_user_groups({'directory_group': 'adobe_group'}, dc)
    assert directory_users is not None

