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

import okta
import six
import string
from okta.framework.OktaError import OktaError

import user_sync.connector.helper
import user_sync.helper
import user_sync.identity_type
from user_sync.connector.directory import DirectoryConnector
from user_sync.config.common import DictConfig, OptionsBuilder
from user_sync.error import AssertionException
from user_sync.config import user_sync as config
from user_sync.config import common as config_common


class OktaDirectoryConnector(DirectoryConnector):
    name = 'okta'

    def __init__(self, caller_options, *args, **kwargs):
        super(OktaDirectoryConnector, self).__init__(*args, **kwargs)
        caller_config = DictConfig('%s configuration' % self.name, caller_options)
        builder = OptionsBuilder(caller_config)
        builder.set_string_value('group_filter_format',
                                 '{group}')
        builder.set_string_value('all_users_filter',
                                 'user.status == "ACTIVE"')
        builder.set_string_value('string_encoding', 'utf8')
        builder.set_string_value('user_identity_type_format', None)
        builder.set_string_value('user_email_format', six.text_type('{email}'))
        builder.set_string_value('user_username_format', None)
        builder.set_string_value('user_domain_format', None)
        builder.set_string_value('user_given_name_format', six.text_type('{firstName}'))
        builder.set_string_value('user_surname_format', six.text_type('{lastName}'))
        builder.set_string_value('user_country_code_format', six.text_type('{countryCode}'))
        builder.set_string_value('user_identity_type', None)
        builder.set_string_value('logger_name', self.name)
        host = builder.require_string_value('host')
        api_token = builder.require_string_value('api_token')

        options = builder.get_options()

        OKTAValueFormatter.encoding = options['string_encoding']
        self.user_identity_type = user_sync.identity_type.parse_identity_type(options['user_identity_type'])
        self.user_identity_type_formatter = OKTAValueFormatter(options['user_identity_type_format'])
        self.user_email_formatter = OKTAValueFormatter(options['user_email_format'])
        self.user_username_formatter = OKTAValueFormatter(options['user_username_format'])
        self.user_domain_formatter = OKTAValueFormatter(options['user_domain_format'])
        self.user_given_name_formatter = OKTAValueFormatter(options['user_given_name_format'])
        self.user_surname_formatter = OKTAValueFormatter(options['user_surname_format'])
        self.user_country_code_formatter = OKTAValueFormatter(options['user_country_code_format'])

        self.users_client = None
        self.groups_client = None
        self.logger = logger = user_sync.connector.helper.create_logger(options)
        self.user_identity_type = user_sync.identity_type.parse_identity_type(options['user_identity_type'])
        self.options = options
        caller_config.report_unused_values(logger)

        if not host.startswith('https://'):
            if "://" in host:
                raise AssertionException("Okta protocol must be https")
            host = "https://" + host

        self.user_by_uid = {}

        logger.debug('%s initialized with options: %s', self.name, options)

        logger.info('Connecting to: %s', host)

        try:
            self.users_client = okta.UsersClient(host, api_token)
            self.groups_client = okta.UserGroupsClient(host, api_token)
        except OktaError as e:
            raise AssertionException("Error connecting to Okta: %s" % e)

        logger.info('Connected')

    def load_users_and_groups(self, groups, extended_attributes, all_users):
        """
        :type groups: list(str)
        :type extended_attributes: list(str)
        :type all_users: bool
        :rtype (bool, iterable(dict))
        """
        if all_users:
            raise AssertionException("Okta connector has no notion of all users, please specify a --users group")

        options = self.options
        all_users_filter = options['all_users_filter']

        self.logger.info('Loading users...')
        self.user_by_uid = user_by_uid = {}

        for group in groups:
            total_group_members = 0
            total_group_users = 0
            for user in self.iter_group_members(group, all_users_filter, extended_attributes):
                total_group_members += 1

                uid = user.get('uid')
                if user and uid:
                    if uid not in user_by_uid:
                        user_by_uid[uid] = user
                    total_group_users += 1
                    user_groups = user_by_uid[uid]['groups']
                    if group not in user_groups:
                        user_groups.append(group)

            self.logger.debug('Group %s members: %d users: %d', group, total_group_members, total_group_users)

        return six.itervalues(user_by_uid)

    def find_group(self, group):
        """
        :type group: str
        :rtype UserGroup
        """
        group = group.strip()
        options = self.options
        group_filter_format = options['group_filter_format']
        try:
            results = self.groups_client.get_groups(query=group_filter_format.format(group=group))
        except KeyError as e:
            raise AssertionException("Bad format key in group query (%s): %s" % (group_filter_format, e))
        except OktaError as e:
            self.logger.warning("Unable to query group")
            raise AssertionException("Okta error querying for group: %s" % e)

        if results is None:
            self.logger.warning("No group found for: %s", group)
        else:
            for result in results:
                if result.profile.name == group:
                    return result

        return None

    def iter_group_members(self, group, filter_string, extended_attributes):
        """
        :type group: str
        :type filter_string: str
        :type extended_attributes: list
        :rtype iterator(str, str)
        """

        user_attribute_names = []
        user_attribute_names.extend(self.user_given_name_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_surname_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_country_code_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_identity_type_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_email_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_username_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_domain_formatter.get_attribute_names())
        extended_attributes = list(set(extended_attributes) - set(user_attribute_names))
        user_attribute_names.extend(extended_attributes)

        res_group = self.find_group(group)
        if res_group:
            try:
                attr_dict = OKTAValueFormatter.get_extended_attribute_dict(user_attribute_names)
                members = self.groups_client.get_group_all_users(res_group.id, attr_dict)
            except OktaError as e:
                self.logger.warning("Unable to get_group_users")
                raise AssertionException("Okta error querying for group users: %s" % e)
            # Filtering users based all_users_filter query in config
            for member in self.filter_users(members, filter_string):
                user = self.convert_user(member, extended_attributes)
                if not user:
                    continue
                yield (user)
        else:
            self.logger.warning("No group found for: %s", group)

    def convert_user(self, record, extended_attributes):

        source_attributes = {}
        source_attributes['login'] = login = OKTAValueFormatter.get_profile_value(record,'login')
        email, last_attribute_name = self.user_email_formatter.generate_value(record)
        email = email.strip() if email else None
        if not email:
            if last_attribute_name is not None:
                self.logger.warning('Skipping user with login %s: empty email attribute (%s)', login, last_attribute_name)
            return None
        user = user_sync.connector.helper.create_blank_user()
        source_attributes['id'] = user['uid'] = record.id
        source_attributes['email'] = email
        user['email'] = email

        source_attributes['identity_type'] = user_identity_type = self.user_identity_type
        if not user_identity_type:
            user['identity_type'] = self.user_identity_type
        else:
            try:
                user['identity_type'] = user_sync.identity_type.parse_identity_type(user_identity_type)
            except AssertionException as e:
                self.logger.warning('Skipping user %s: %s', login, e)
                return None



        username, last_attribute_name = self.user_username_formatter.generate_value(record)
        username = username.strip() if username else None
        source_attributes['username'] = username
        if username:
            user['username'] = username
        else:
            if last_attribute_name:
                self.logger.warning('No username attribute (%s) for user with login: %s, default to email (%s)',
                                    last_attribute_name, login, email)
            user['username'] = email

        domain, last_attribute_name = self.user_domain_formatter.generate_value(record)
        domain = domain.strip() if domain else None
        source_attributes['domain'] = domain
        if domain:
            user['domain'] = domain
        elif username != email:
            user['domain'] = email[email.find('@') + 1:]
        elif last_attribute_name:
            self.logger.warning('No domain attribute (%s) for user with login: %s', last_attribute_name, login)

        first_name_value, last_attribute_name = self.user_given_name_formatter.generate_value(record)
        source_attributes['firstName'] = first_name_value
        if first_name_value is not None:
            user['firstname'] = first_name_value
        elif last_attribute_name:
            self.logger.warning('No given name attribute (%s) for user with login: %s', last_attribute_name, login)
        last_name_value, last_attribute_name = self.user_surname_formatter.generate_value(record)
        source_attributes['lastName'] = last_name_value
        if last_name_value is not None:
            user['lastname'] = last_name_value
        elif last_attribute_name:
            self.logger.warning('No last name attribute (%s) for user with login: %s', last_attribute_name, login)
        country_value, last_attribute_name = self.user_country_code_formatter.generate_value(record)
        source_attributes['c'] = country_value
        if country_value is not None:
            user['country'] = country_value.upper()
        elif last_attribute_name:
            self.logger.warning('No country code attribute (%s) for user with login: %s', last_attribute_name, login)

        if extended_attributes is not None:
            for extended_attribute in extended_attributes:
                extended_attribute_value = OKTAValueFormatter.get_profile_value(record, extended_attribute)
                source_attributes[extended_attribute] = extended_attribute_value

        user['source_attributes'] = source_attributes.copy()
        return user

    def iter_search_result(self, filter_string, attributes):
        """
        type: filter_string: str
        type: attributes: list(str)
        """

        attr_dict = OKTAValueFormatter.get_extended_attribute_dict(attributes)

        try:
            self.logger.info("Calling okta SDK get_users with the following %s", filter_string)
            if attr_dict:
                users = self.users_client.get_all_users(query=filter_string, extended_attribute=attr_dict)
            else:
                users = self.users_client.get_all_users(query=filter_string)
        except OktaError as e:
            self.logger.warning("Unable to query users")
            raise AssertionException("Okta error querying for users: %s" % e)
        return users

    def filter_users(self, users, filter_string):
        # Allow the following builtin functions to be used in eval()
        whitelist = {
            "len": len, "int": int, "float": float, "str": str, "enumerate": enumerate, "filter": filter,
            "getattr": getattr, "hasattr": hasattr, "list": list, "map": map, "max": max, "min": min,
            "range": range, "sorted": sorted, "sum": sum, "tuple": tuple, "zip": zip
        }

        try:
            return list(filter(lambda user: eval(filter_string, {"__builtins__": whitelist}, {"user": user}), users))
        except SyntaxError as e:
            raise AssertionException("Invalid syntax in predicate (%s): cannot evaluate" % filter_string)
        except Exception as e:
            raise AssertionException("Error filtering with predicate (%s): %s" % (filter_string, e))


class OKTAValueFormatter(object):
    encoding = 'utf8'

    def __init__(self, string_format):
        """
        The format string must be a unicode or ascii string: see notes above about being careful in Py2!
        """
        if string_format is None:
            attribute_names = []
        else:
            string_format = six.text_type(string_format)  # force unicode so attribute values are unicode
            formatter = string.Formatter()
            attribute_names = [six.text_type(item[1]) for item in formatter.parse(string_format) if item[1]]
        self.string_format = string_format
        self.attribute_names = attribute_names

    def get_attribute_names(self):
        """
        :rtype list(str)
        """
        return self.attribute_names

    @staticmethod
    def get_extended_attribute_dict(attributes):

        attr_dict = {}
        for attribute in attributes:
            if attribute not in attr_dict:
                attr_dict.update({attribute: str})

        return attr_dict

    def generate_value(self, record):
        """
        :type record: dict
        :rtype (unicode, unicode)
        """
        result = None
        attribute_name = None
        if self.string_format is not None:
            values = {}
            for attribute_name in self.attribute_names:
                value = self.get_profile_value(record, attribute_name)
                if value is None:
                    values = None
                    break
                values[attribute_name] = value
            if values is not None:
                result = self.string_format.format(**values)
        return result, attribute_name

    @classmethod
    def get_profile_value(cls, record, attribute_name):
        """
        The attribute value type must be decodable (str in py2, bytes in py3)
        :type record: okta.models.user.User
        :type attribute_name: unicode
        """
        if hasattr(record.profile, attribute_name):
            attribute_values = getattr(record.profile,attribute_name)
            if attribute_values:
                try:
                    return attribute_values
                except UnicodeError as e:
                    raise AssertionException("Encoding error in value of attribute '%s': %s" % (attribute_name, e))
        return None
