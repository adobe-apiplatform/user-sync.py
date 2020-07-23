import logging
from user_sync.config.sign_sync import SignConfigLoader
from user_sync.config.user_sync import DictConfig


def test_loader_attributes(sign_config_file):
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    assert isinstance(config.logger, logging.Logger)
    assert config.args == args
    assert config.invocation_options == {'users': ['mapped']}
    assert isinstance(config.main_config, DictConfig)
