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

from sign_client.model import DetailedGroupInfo, GroupInfo, DetailedUserInfo, UserGroupsInfo, UserStateInfo
from sign_client.error import AssertionException as ClientException

from ..config.common import DictConfig, OptionsBuilder
from ..cache.sign import SignCache
from ..error import AssertionException
from sign_client.client import SignClient
from pathlib import Path


class SignConnector(object):

    def __init__(self, caller_options, org_name, test_mode, connection, cache_config):
        """
        :type caller_options: dict
        """
        self.console_org = org_name
        self.name = 'sign_{}'.format(self.console_org)
        self.logger = logging.getLogger(self.name)
        self.test_mode = test_mode
        caller_config = DictConfig('sign_configuration', caller_options)
        sign_builder = OptionsBuilder(caller_config)
        sign_builder.require_string_value('host')
        sign_builder.require_string_value('admin_email')
        self.create_users = sign_builder.require_value('create_users', bool)
        self.deactivate_users = sign_builder.require_value('deactivate_users', bool)
        store_path = Path(cache_config['path'])

        options = sign_builder.get_options()
        integration_key = caller_config.get_credential('integration_key', options['admin_email'])
        caller_config.report_unused_values(self.logger)

        if store_path is None:
            raise AssertionException(f"Cache path must be specified in '{org_name}' connector config")

        self.cache = SignCache(Path(store_path), org_name)

        self.sign_client = SignClient(connection,
                                      host=options['host'],
                                      integration_key=integration_key,
                                      admin_email=options['admin_email'],
                                      logger=self.logger)

    def sign_groups(self):
        if self.cache.should_refresh:
            self.refresh_all()
        return {g.groupName.lower(): g for g in self.cache.get_groups()}

    def create_group(self, new_group: DetailedGroupInfo):
        if not self.test_mode:
            group_id = self.sign_client.create_group(new_group)
            self.cache.cache_group(GroupInfo(
                groupId=group_id,
                groupName=new_group.name,
            ))

    def get_users(self):
        if self.cache.should_refresh:
            self.refresh_all()

        # always refresh individual users that may need it
        users_to_refresh = self.cache.get_users_to_refresh()
        if users_to_refresh:
            for user in self.sign_client.get_users([u.id for u in users_to_refresh]).values():
                self.cache.update_user(user)
                self.cache.update_user_refresh_status(user.id, needs_refresh=False)

        return {user.id: user for user in self.cache.get_users()}

    def get_user_groups(self):
        if self.cache.should_refresh:
            self.refresh_all()
        return dict(self.cache.get_user_groups())

    def update_users(self, update_data: list[DetailedUserInfo]):
        if not self.test_mode:
            self.sign_client.update_users(update_data)
            for user in update_data:
                self.cache.update_user(user)

    def update_user_groups(self, update_data: list[tuple[str, UserGroupsInfo]]):
        if not self.test_mode:
            self.sign_client.update_user_groups(update_data)
            for user_id, user_groups in update_data:
                self.cache.update_user_groups(user_id, user_groups.groupInfoList)

    def update_user_group_single(self, user_id: str, update_data: UserGroupsInfo):
        if not self.test_mode:
            self.sign_client.update_user_groups_single(user_id, update_data)
            self.cache.update_user_groups(user_id, update_data.groupInfoList)

    def get_group(self, assignment_group):
        return [g.groupId for g in self.sign_client.groups if g.groupName.lower() == assignment_group.lower()][0]

    def insert_user(self, new_user: DetailedUserInfo)-> str:
        if not self.test_mode:
            user_id = self.sign_client.insert_user(new_user)
            new_user.id = user_id
            self.cache.cache_user(new_user)
            return user_id

    def update_user_state(self, user_id, state: UserStateInfo):
        if not self.test_mode:
            try:
                self.sign_client.update_user_state(user_id, state)
            except ClientException:
                # The API won't let us manage all user states, so we need to flag the record
                # for refresh if we get any errors. That way state can be rechecked next time in case
                # it changed in the application
                self.cache.update_user_refresh_status(user_id, needs_refresh=True)
                raise
            user = self.cache.get_user(user_id)
            user.status = state.state
            self.cache.update_user(user)
    
    def refresh_all(self):
        self.cache.clear_all()
        self.refresh_users()
        self.refresh_groups()
        self.refresh_user_groups()
        self.cache.should_refresh = False
        self.cache.update_next_refresh()
    
    def refresh_users(self):
        for user in self.sign_client.get_users().values():
            self.cache.cache_user(user)
    
    def refresh_groups(self):
        for group in self.sign_client.sign_groups():
            self.cache.cache_group(group)

    def refresh_user_groups(self):
        user_ids = [u.id for u in self.cache.get_users()]
        for user_id, user_groups in self.sign_client.get_user_groups(user_ids).items():
            for user_group in user_groups.groupInfoList:
                self.cache.cache_user_group(user_id, user_group)
