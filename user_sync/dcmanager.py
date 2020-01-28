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


class DirectoryConnectorManager(object):
    def __init__(self, config_loader, additional_groups, default_account_type):
        self.logger = logging.getLogger("dc manager")
        self.config_loader = config_loader
        self.additional_groups = additional_groups
        self.new_account_type = default_account_type
        self.connectors = {}

        for k, v in six.iteritems(self.get_directory_connector_config()):
            self.connectors[k] = self.build_connector(v)

    def get_directory_connector_config(self):

        config_dict = {}
        for i in self.config_loader.get_directory_connector_configs():
            caller = DictConfig("connectors", i)
            builder = OptionsBuilder(caller)
            builder.require_string_value('id')
            builder.require_string_value('path')
            builder.require_string_value('type')
            caller.report_unused_values(self.logger)
            options = builder.get_options()
            conn_id = options['id']

            if conn_id in config_dict:
                raise AssertionException("Connector id: '{}' is already defined".format(conn_id))
            config_dict[conn_id] = options
        return config_dict

    def build_connector(self, config):

        directory_connector = None
        directory_connector_options = None
        directory_connector_module_name = self.config_loader.get_directory_connector_module_name(config['type'])
        if directory_connector_module_name is not None:
            directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])
            directory_connector = DirectoryConnector(directory_connector_module)
            directory_connector_options = self.config_loader.get_directory_connector_options(config['path'])

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

    def load_users_and_groups(self, groups, extended_attributes, all_users):

        users = {}
        for c,v in six.iteritems(self.connectors):
            z = v.load_users_and_groups(groups, extended_attributes, all_users)

            for k in z:
                users[k['email']] = k
        return six.itervalues(users)
