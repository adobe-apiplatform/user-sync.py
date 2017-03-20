# Copyright (c) 2016-2017 Adobe Systems Incorporated.  All rights reserved.
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

import user_sync.config
import user_sync.connector.helper
import user_sync.error
import user_sync.helper
import user_sync.identity_type
import okta.UserGroupsClient
import okta.UsersClient
import string


def connector_metadata():
    metadata = {
        'name': OktaDirectoryConnector.name
    }
    return metadata


def connector_initialize(options):
    '''
    :type options: dict
    '''
    state = OktaDirectoryConnector(options)
    return state


def connector_load_users_and_groups(state, groups, extended_attributes):
    '''
    :type state: OktaDirectoryConnector
    :type groups: list(str)
    :type extended_attributes: list(str)
    :rtype (bool, iterable(dict))
    '''

    # CSV supports arbitrary aka "extended" attrs by default, so the value of extended_attributes has no impact on this particular connector

    return state.load_users_and_groups(groups, extended_attributes)


class OktaDirectoryConnector(object):
    name = 'okta'

    def __init__(self, caller_options):
        caller_config = user_sync.config.DictConfig('"%s options"' % OktaDirectoryConnector.name, caller_options)
        builder = user_sync.config.OptionsBuilder(caller_config)
        builder.set_string_value('group_filter_format',
                                 '{group}')
        builder.set_string_value('all_users_filter',
                                 'status eq "ACTIVE"')
        #builder.set_string_value('user_email_format', '{email}')
        builder.set_string_value('user_identity_type', None)
        builder.set_string_value('logger_name', 'connector.' + OktaDirectoryConnector.name)
        builder.set_dict_value('source_filters', {})

        okta_url = "https://" + builder.require_string_value('okta_url')
        api_token = builder.require_string_value('api_token')

        options = builder.get_options()

        #self.user_email_formatter = OKTAValueFormatter(options['user_email_format'])

        self.users_client = None
        self.groups_client = None
        self.logger = logger = user_sync.connector.helper.create_logger(options)

        try:
            options['user_identity_type'] = user_sync.identity_type.parse_identity_type(options['user_identity_type'])
        except user_sync.error.AssertionException as e:
            logger.error(e.message)
            e.set_reported()
            raise e

        self.options = options

        logger.debug('Initialized with options: %s', options)

        logger.info('Connecting to: %s', okta_url)

        try:
            self.users_client = okta.UsersClient(okta_url, api_token)
            self.groups_client = okta.UserGroupsClient(okta_url, api_token)
        except Exception as e:
            raise user_sync.error.AssertionException(repr(e))

        logger.info('Connected')

    def load_users_and_groups(self, groups, extended_attributes):
        '''
        :type groups: list(str)
        :type extended_attributes: list(str)
        :rtype (bool, iterable(dict))
        '''
        options = self.options
        all_users_filter = options['all_users_filter']

        is_using_source_filter = False
        source_filters = options['source_filters']
        source_filter = source_filters.get('all_users_filter')
        if (source_filter != None):
            users_filter = "(%s) and (%s)" % (all_users_filter, source_filter)
            is_using_source_filter = True
            self.logger.info('Applied source filter: %s', users_filter)
        else:
            users_filter = all_users_filter

        self.logger.info('Loading users...')

        self.user_by_login = user_by_login = {}
        self.user_by_uid = user_by_uid = {}
        for user_login, user in self.iter_users(users_filter, extended_attributes):
            uid = user.get("uid")
            if (id != None):
                user_by_uid[uid] = user
            user_by_login[user_login] = user

        self.logger.info('Total users loaded: %d', len(user_by_login))

        for group in groups:
            total_group_members = 0
            total_group_users = 0
            group_members = self.iter_group_members(group)
            for group_member_uid in group_members:
                total_group_members += 1

                user = user_by_uid.get(group_member_uid)
                if (user != None):
                    total_group_users += 1
                    user_groups = user['groups']
                    if not group in user_groups:
                        user_groups.append(group)
            self.logger.debug('Group %s members: %d users: %d', group, total_group_members, total_group_users)

        return (not is_using_source_filter, user_by_uid.itervalues())

    def find_group(self, group):
        '''
        :type group: str
        :type attribute_list: list(str)
        :rtype (str, dict)
        '''
        options = self.options
        group_filter_format = options['group_filter_format']
        try:
            res = self.groups_client.get_groups(query=group_filter_format.format(group=group))
        except Exception as e:
            self.logger.warning("Unable to query group")
            raise user_sync.error.AssertionException(repr(e))

        if (len(res) < 1):
            raise user_sync.error.AssertionException("Group not found for: %s" % group)
        elif (len(res) > 1):
            raise user_sync.error.AssertionException("Multiple groups found for: %s" % group)

        return res[0]

    def iter_group_members(self, group):
        '''
        :type group: str
        :rtype iterator(str, str)
        '''
        res_group = self.find_group(group)
        if (res_group != None):
            try:
                members = self.groups_client.get_group_users(res_group.id)
            except Exception as e:
                self.logger.warning("Unable to get_group_users")
                raise user_sync.error.AssertionException(repr(e))
            for member in members:
                yield (member.id)
        else:
            self.logger.warning("No group found for: %s", group)

    def iter_users(self, users_filter, extended_attributes):
        options = self.options

        ###TODO does nothing for now
        user_attribute_names = ["firstName", "lastName","login","email","countryCode"]
        #user_attribute_names.extend(self.user_email_formatter.get_attribute_names())

        extended_attributes = list(set(extended_attributes) - set(user_attribute_names))
        user_attribute_names.extend(extended_attributes)
        ###

        result_iter = self.iter_search_result(users_filter, user_attribute_names)

        for record in result_iter:
            profile = record.profile
            if (profile.email == None):
                # if (last_attribute_name != None):
                self.logger.warn('No email attribute for login: %s', profile.login)
                continue

            source_attributes = {}
            user = user_sync.connector.helper.create_blank_user()

            source_attributes['id'] = user['uid'] = record.id
            source_attributes['email'] = user['email'] = profile.email
            source_attributes['login'] = user['username'] = profile.login

            if profile.firstName != None:
                source_attributes['firstName'] = user['firstname'] = profile.firstName
            else:
                source_attributes['firstName'] = None

            if profile.lastName != None:
                source_attributes['lastName'] = user['lastname'] = profile.lastName
            else:
                source_attributes['lastName'] = None

            if profile.countryCode != None:
                source_attributes['countryCode'] = user['country'] = profile.countryCode
            else:
                source_attributes['countryCode'] = None

            if extended_attributes is not None:
                for extended_attribute in extended_attributes:
                    if extended_attribute not in source_attributes:
                        if(hasattr(profile,extended_attribute)):
                            extended_attribute_value = getattr(profile,extended_attribute)
                            source_attributes[extended_attribute] = extended_attribute_value
                        else:
                            source_attributes[extended_attribute] = None

            # [TODO morr 2017-02-26]: Could be omitted if no hook; worth considering?
            # [TODO morr 2017-02-28]: Is the copy necessary? Could just assign I think
            user['source_attributes'] = source_attributes.copy()

            yield (profile.login, user)

    def iter_search_result(self, filter_string, attributes):
        '''
        type: filter_string: str
        type: attributes: list(str)
        '''

        attr_dict = OKTAValueFormatter.get_extended_attribute_dict(attributes)

        try:
            self.logger.info("Calling okta SDK get_users with the following %s", filter_string)
            if attr_dict:
                users = self.users_client.get_users(query=filter_string, extended_attribute=attr_dict)
            else:
                users = self.users_client.get_users(query=filter_string)
        except Exception as e:
            self.logger.warning("Unable to query users")
            raise user_sync.error.AssertionException(repr(e))
        return users




class OKTAValueFormatter(object):

    @staticmethod
    def get_extended_attribute_dict(attributes):

        attr_dict = {}
        for attribute in attributes:
            if attribute not in attr_dict:
                attr_dict.update({attribute:str})

        return attr_dict