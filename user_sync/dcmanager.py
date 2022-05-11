# Copyright (c) 2016-2017 Adobe Inc.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging

from user_sync import identity_type
from user_sync.config.common import DictConfig, OptionsBuilder
from user_sync.connector.directory import DirectoryConnector
from user_sync.error import AssertionException
from .connector.directory_adobe_console import AdobeConsoleConnector
from .connector.directory_csv import CSVDirectoryConnector
from .connector.directory_ldap import LDAPDirectoryConnector
from .connector.directory_okta import OktaDirectoryConnector


class DirectoryConnectorConfig(object):

    def __init__(self, **options):

        logger = logging.getLogger()
        caller = DictConfig("connector_config", options)
        builder = OptionsBuilder(caller)
        builder.require_string_value('type')
        builder.set_string_value('id', None)
        builder.set_string_value('path', None)

        caller.report_unused_values(logger)
        options = builder.get_options()

        # Shortcut for specifying connectors by type and path only
        if options['id'] is None:
            options['id'] = options['type']

        # All connectors except CSV require a path (because CSV can be used with --users file)
        if not options['path'] and options['id'] != 'users-file':
            raise AssertionException("Config path is required for connectors of type '{}'".format(options['type']))

        self.id = options['id']
        self.type = options['type']
        self.path = options['path']


class DirectoryConnectorManager(object):
    connector_classes = {
        'ldap': LDAPDirectoryConnector,
        'csv': CSVDirectoryConnector,
        'okta': OktaDirectoryConnector,
        'adobe_console': AdobeConsoleConnector,
    }

    def __init__(self, config_loader, additional_groups=None, default_account_type=None):
        self.logger = logging.getLogger("dc manager")
        self.config_loader = config_loader
        self.additional_groups = additional_groups or []
        self.new_account_type = default_account_type or identity_type.FEDERATED_IDENTITY_TYPE
        self.connectors = {}
        self.is_multi = config_loader.invocation_options['connector'] == ['multi']

        for k, v in self.build_directory_config_dict().items():
            self.connectors[k] = self.build_connector(v)

    def build_directory_config_dict(self):

        config_dict = {}
        if self.config_loader.invocation_options.get('users-file'):
            config_dict['users-file'] = DirectoryConnectorConfig(id='users-file', type='csv')
        else:
            for i in self.config_loader.get_directory_connector_configs():
                conf = DirectoryConnectorConfig(**i)
                if conf.id in config_dict:
                    raise AssertionException("Connector id: '{}' is already defined".format(conf.id))
                config_dict[conf.id] = conf

        return config_dict

    def build_connector(self, config):
        directory_connector = None
        directory_connector_options = None
        directory_connector_module_name = self.config_loader.get_directory_connector_module_name(config.type)
        if directory_connector_module_name not in self.connector_classes:
            raise AssertionException(f"Connector type '{directory_connector_module_name}' is not valid")

        directory_connector_options = self.config_loader.get_directory_connector_options(config.path)
        if directory_connector_options is not None:
            directory_connector_options['user_identity_type'] = self.new_account_type

        directory_connector = self.connector_classes[directory_connector_module_name](directory_connector_options)

        additional_group_filters = None
        if self.additional_groups and isinstance(self.additional_groups, list):
            additional_group_filters = [r['source'] for r in self.additional_groups]

        directory_connector.additional_group_filters = additional_group_filters

        # show error dynamic mappings enabled but 'dynamic_group_member_attribute' is not defined
        if additional_group_filters and directory_connector.options['dynamic_group_member_attribute'] is None:
            raise AssertionException(
                "Failed to enable dynamic group mappings. 'dynamic_group_member_attribute' is not defined in config")

        return directory_connector

    def build_directory_groups(self, group_names):
        # If multi connector is not used, assume all group names are literal
        groups = [DirectoryGroup(g, literal=(not self.is_multi)) for g in group_names]
        for g in groups:
            if g.directory_id not in self.connectors and g.directory_id is not None:
                raise AssertionException("Missing connector {0} for group mapping: {1}".format(g.directory_id, g.fq_name))
        return groups

    def load_users_and_groups(self, groups, extended_attributes, all_users):
        users = []
        dir_groups = self.build_directory_groups(groups)
        global_groups = self.common_names_for_connector(dir_groups, None)

        for c, v in self.connectors.items():
            self.logger.info("Loading users from connector: " + "id: " + c + "   type: " + v.name)
            common_names = global_groups.copy().union(self.common_names_for_connector(dir_groups, c))
            new_users = list(v.load_users_and_groups(common_names, extended_attributes, all_users))
            self.logger.info("Found {} users".format(len(new_users)))
            for u in new_users:
                self.substitute_groups_for_user(u, dir_groups)
            users.extend(new_users)
        return iter(users)

    @staticmethod
    def list_to_map(obj_list, field):
        result = {}
        for o in obj_list:
            key = getattr(o, field)
            if key not in result:
                result[key] = [o]
            else:
                result[key].append(o)
        return result

    @staticmethod
    def common_names_for_connector(groups, id):
        groups_by_id = DirectoryConnectorManager.list_to_map(groups, 'directory_id')
        return {g.common_name for g in groups_by_id.get(id, [])}

    @staticmethod
    def substitute_groups_for_user(user, groups):
        groups_by_cn = DirectoryConnectorManager.list_to_map(groups, 'common_name')
        qualified_groups = []
        for g in user['groups']:
            if g in groups_by_cn:
                qualified_groups.extend([g.fq_name for g in groups_by_cn[g]])
            else:
                qualified_groups.append(g)
        user['groups'] = qualified_groups

class DirectoryGroup:

    def __init__(self, fq_name, literal=False):
        self.fq_name = fq_name
        self.directory_id = None
        self.common_name = fq_name

        # if literal is specified, treat the group name as a literal string
        # in this case, fq_name = common_name
        if literal:
            return

        tokens = fq_name.split('::')
        if len(tokens) > 1:
            self.directory_id = tokens[0]
            self.common_name = "::".join(tokens[1:])
            self.fq_name = fq_name
