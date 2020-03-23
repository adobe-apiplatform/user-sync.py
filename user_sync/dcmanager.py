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

import six

from user_sync.config import DictConfig, OptionsBuilder
from user_sync.connector.directory import DirectoryConnector
from user_sync.error import AssertionException
from collections import Counter

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

    def __init__(self, config_loader, additional_groups, default_account_type):
        self.logger = logging.getLogger("dc manager")
        self.config_loader = config_loader
        self.additional_groups = additional_groups
        self.new_account_type = default_account_type
        self.connectors = {}

        for k, v in six.iteritems(self.build_directory_config_dict()):
            self.connectors[k] = self.build_connector(v)

    def build_directory_config_dict(self):

        config_dict = {}
        if self.config_loader.invocation_options.get('users-file'):
                config_dict['users-file'] = DirectoryConnectorConfig(id='users-file',type='csv')
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
        if directory_connector_module_name is not None:
            directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])
            directory_connector = DirectoryConnector(directory_connector_module)
            directory_connector_options = self.config_loader.get_directory_connector_options(config.path)

        if directory_connector is not None and directory_connector_options is not None:
            # specify the default user_identity_type if it's not already specified in the options
            if 'user_identity_type' not in directory_connector_options:
                directory_connector_options['user_identity_type'] = self.new_account_type
                directory_connector.initialize(directory_connector_options)

        additional_group_filters = None
        if self.additional_groups and isinstance(self.additional_groups, list):
            additional_group_filters = [r['source'] for r in self.additional_groups]
        if directory_connector is not None:
            directory_connector.state.additional_group_filters = additional_group_filters

        return directory_connector

    def get_groups_for_connector(self, id, group_list):
        for i in range(len(group_list)):
            return {g.common_name for g in group_list if (g.directory_id == id or g.directory_id is None)}

    def add_on_groups(self, groups):
        additional_groups = set()
        for g in groups:
            for x in groups[1:]:
                if g.common_name == x.common_name and g.directory_id != x.directory_id and (g.directory_id is None or x.directory_id is None):
                        additional_groups.add(g.common_name)
        return additional_groups

    def update_groups_for_user(self, user, groups, source_id, additional_groups):
        list_of_groups = user['groups']
        for i in range(len(user['groups'])):
            for g in groups:
                if user['groups'][i] == g.common_name and g.directory_id is not None and source_id == g.directory_id:
                    list_of_groups[i] = g.directory_id + "::" + user['groups'][i]
                    if g.common_name in additional_groups:
                        list_of_groups.append(g.common_name)
                    break
            user['groups'] = list_of_groups
        return user

    def load_users_and_groups(self, groups, extended_attributes, all_users):
        group_list = []
        users = []
        for g in groups:
            group_list.append(DirectoryGroup(g))
        add_groups = self.add_on_groups(group_list)
        for c,v in six.iteritems(self.connectors):
            self.logger.info("Loading users from connector: " + "id: " + c + "   type: " + v.name)
            dir_groups = self.get_groups_for_connector(c, group_list)
            new_users = list(v.load_users_and_groups(dir_groups, extended_attributes, all_users))
            self.logger.info("Found {} users".format(len(new_users)))
            for u in new_users:
                self.update_groups_for_user(u, group_list, c, add_groups)
            users.extend(new_users)
        return iter(users)


class DirectoryGroup:

    def __init__(self, fq_name):
        self.fq_name = fq_name
        self.directory_id = None
        self.common_name = fq_name
        tokens = fq_name.split('::')

        if len(tokens) > 1:
            self.directory_id = tokens[0]
            self.common_name = "::".join(tokens[1:])
            self.fq_name = fq_name
