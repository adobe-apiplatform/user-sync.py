import logging
import codecs

from copy import deepcopy
from collections import defaultdict
from typing import Dict
from schema import Schema

from user_sync.config.common import DictConfig, ConfigLoader, ConfigFileLoader, resolve_invocation_options
from user_sync.error import AssertionException
from user_sync.engine.common import AdobeGroup
from .error import ConfigValidationError


def config_schema() -> Schema:
    from schema import And, Optional, Or, Regex
    return Schema({
        'sign_orgs': { str: str },
        'identity_source': {
            'connector': And(str, len),
            'type': Or('csv', 'okta', 'ldap', 'adobe_console'), #TODO: single "source of truth" for these options
        },
        'user_sync': {
            'create_users': bool,
            'sign_only_limit': Or(int, Regex(r'^\d+%$')),
        },
        'user_management': [{
            'directory_group': Or(None, And(str, len)),
            'sign_group': Or(None, And(str, len)),
            'admin_role': Or(None, 'GROUP_ADMIN', 'ACCOUNT_ADMIN'), #TODO: single "source of truth" for these options
        }],
        'logging': {
            'log_to_file': bool,
            'file_log_directory': And(str, len),
            'file_log_name_format': And(str, len),
            'file_log_level': Or('info', 'debug'), #TODO: what are the valid values here?
            'console_log_level': Or('info', 'debug'), #TODO: what are the valid values here?
        },
        'invocation_defaults': {
            'users': Or('mapped', 'all'), #TODO: single "source of truth" for these options
        }
    })


class SignConfigLoader(ConfigLoader):
    """
    Loads config files and does pathname expansion on settings that refer to files or directories
    """
    # key_paths in the root configuration file that should have filename values
    # mapped to their value options.  See load_from_yaml for the option meanings.
    ROOT_CONFIG_PATH_KEYS = {'/sign_orgs/*': (True, False, None),
                             '/identity_source/connector': (True, False, None),
                             '/logging/file_log_directory': (False, False, "sign_logs"),
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
        filename, encoding = self._config_file_info()
        self.raw_config = self._load_raw_config(filename, encoding)
        self._validate(self.raw_config)
        self.main_config = self.load_main_config(filename, self.raw_config)
        self.invocation_options = self.load_invocation_options()
    
    def load_invocation_options(self) -> dict:
        options = deepcopy(self.invocation_defaults)
        invocation_config = self.main_config.get_dict_config('invocation_defaults', True)
        options = resolve_invocation_options(options, invocation_config, self.invocation_defaults, self.args)
        return options

    def load_main_config(self, filename, content) -> DictConfig:
        return DictConfig("<%s>" % filename, content)
    
    def _config_file_info(self) -> (str, str):
        filename = self.args.get('config_filename') or self.config_defaults['config_filename']
        encoding = self.args.get('encoding_name') or self.config_defaults['config_encoding']
        try:
            codecs.lookup(encoding)
        except LookupError:
            raise AssertionException("Unknown encoding '%s' specified for configuration files" % encoding)
        return filename, encoding

    def _load_raw_config(self, filename, encoding) -> dict:
        self.logger.info("Using main config file: %s (encoding %s)", filename, encoding)
        config_loader = ConfigFileLoader(encoding, self.ROOT_CONFIG_PATH_KEYS, self.SUB_CONFIG_PATH_KEYS)
        return config_loader.load_root_config(filename)
    
    @staticmethod
    def _validate(raw_config: dict):
        from schema import SchemaError
        try:
            config_schema().validate(raw_config)
        except SchemaError as e:
            raise ConfigValidationError(e.code) from e

    def get_directory_groups(self) -> Dict[str, AdobeGroup]:
        group_mapping = defaultdict(list)
        group_config = self.main_config.get_list_config('user_management', True)
        if group_config is None:
            return group_mapping
        for mapping in group_config.iter_dict_configs():
            dir_group = mapping.get_string('directory_group')
            adobe_group = mapping.get_string('sign_group', True)
            group = AdobeGroup.create(adobe_group)
            if group is None:
                raise AssertionException('Bad Sign group: "{}" in directory group: "{}"'.format(adobe_group, dir_group))
            if group not in group_mapping[dir_group]:
                group_mapping[dir_group].append(group)
        return dict(group_mapping)

    def get_directory_connector_module_name(self):
        pass

    def get_directory_connector_options(self):
        pass

    def check_unused_config_keys(self):
        pass

    def get_logging_config(self):
        pass

    def get_invocation_options(self):
        return self.invocation_options
