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

import json
import logging
import jwt
import six
import user_sync.connector.helper
import user_sync.config.common
import user_sync.helper
import user_sync.identity_type
from user_sync.error import AssertionException
from user_sync.version import __version__ as app_version
from user_sync.connector.client import SignClient

class SignConnector(object):
    def __init__(self, name, caller_options):
        """
        :type name: str
        :type caller_options: dict
        """
        self.name = 'sign' + name
        caller_config = user_sync.config.common.DictConfig(self.name + ' configuration', caller_options)
        sign_builder = user_sync.config.common.OptionsBuilder(caller_config)
        sign_builder.require_string_value('host')
        sign_builder.require_string_value('key')
        sign_builder.require_string_value('admin_email')
        self.option= sign_builder.get_options()
        self.sign_client =   SignClient(self.option)

    def sign_groups(self):
        return self.sign_client.get_groups()
    def create_group(self,new_group):
        return self.sign_client.create_group(new_group)
    def get_users(self):
        return self.sign_client.get_users()
    def update_user(self,user_id,update_data):
        return self.sign_client.update_user(user_id,update_data)
    def get_group(self,assignment_group):
        return self.sign_client.groups.get(assignment_group)
    def get_console_org(self):
        return self.sign_client.console_org















