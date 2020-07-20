import logging
import codecs

from copy import deepcopy

from user_sync.config.common import DictConfig, ConfigFileLoader, resolve_invocation_options
from user_sync.error import AssertionException


class SignConfigLoader:
    """
    Loads config files and does pathname expansion on settings that refer to files or directories
    """
    # key_paths in the root configuration file that should have filename values
    # mapped to their value options.  See load_from_yaml for the option meanings.
    ROOT_CONFIG_PATH_KEYS = {'/adobe_users/connectors/umapi': (True, True, None),
                             '/directory_users/connectors/*': (True, False, None),
                             '/directory_users/extension': (True, False, None),
                             '/logging/file_log_directory': (False, False, "logs"),
                             '/post_sync/connectors/sign_sync': (False, False, False),
                             '/post_sync/connectors/future_feature': (False, False, False)
                             }

    # like ROOT_CONFIG_PATH_KEYS, but for non-root configuration files
    SUB_CONFIG_PATH_KEYS = {'/integration/priv_key_path': (True, False, None)}

    config_defaults = {
        'config_encoding': 'utf8',
        'config_filename': 'sign-sync-config.yml',
    }

    invocation_defaults = {
        'users': ['mapped']
    }

    def __init__(self, args: dict):
        self.logger = logging.getLogger('sign_config')
        self.args = args
        self.main_config = self.load_main_config()
        self.invocation_options = self.load_invocation_options()
    
    def load_invocation_options(self) -> dict:
        options = deepcopy(self.invocation_defaults)
        invocation_config = self.main_config.get_dict_config('invocation_defaults', True)
        options = resolve_invocation_options(options, invocation_config, self.invocation_defaults, self.args)
        return options

    def load_main_config(self) -> DictConfig:
        config_filename = self.args.get('config_filename') or self.config_defaults['config_filename']
        config_encoding = self.args.get('encoding_name') or self.config_defaults['config_encoding']
        try:
            codecs.lookup(config_encoding)
        except LookupError:
            raise AssertionException("Unknown encoding '%s' specified for configuration files" % config_encoding)
        self.logger.info("Using main config file: %s (encoding %s)", config_filename, config_encoding)
        config_loader = ConfigFileLoader(config_encoding, self.ROOT_CONFIG_PATH_KEYS, self.SUB_CONFIG_PATH_KEYS)
        main_config_content = config_loader.load_root_config(config_filename)
        return DictConfig("<%s>" % config_filename, main_config_content)
