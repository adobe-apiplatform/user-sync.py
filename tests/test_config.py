import os
import pytest
from user_sync.config import ConfigFileLoader


@pytest.fixture
def config_file(fixture_dir):
    return os.path.join(fixture_dir, 'user-sync-config.yml')


def test_load_root(config_file):
    """Load root config file and test for presence of root-level keys"""
    config = ConfigFileLoader.load_root_config(config_file)
    assert isinstance(config, dict)
    assert ('adobe_users' in config and 'directory_users' in config and
            'logging' in config and 'limits' in config and
            'invocation_defaults' in config)
