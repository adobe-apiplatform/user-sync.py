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

import umapi_client
import user_sync.connector.helper
import user_sync.helper
import user_sync.identity_type
from user_sync.connector.directory import DirectoryConnector
from user_sync.error import AssertionException
from user_sync.version import __version__ as app_version
from user_sync.connector.umapi_util import create_umapi_auth
from user_sync.helper import normalize_string
from user_sync.identity_type import parse_identity_type
from user_sync.config import user_sync as config
from user_sync.config import common as config_common


class AdobeConsoleConnector(DirectoryConnector):
    name = 'adobe_console'

    def __init__(self, caller_options, *args, **kwargs):
        super(AdobeConsoleConnector, self).__init__(*args, **kwargs)
        self.additional_group_filters = None
        caller_config = config_common.DictConfig('<%s configuration>' % self.name, caller_options)
        builder = config_common.OptionsBuilder(caller_config)
        # Let just ignore this
        builder.set_string_value('user_identity_type', None)
        builder.set_string_value('identity_type_filter', 'all')
        builder.set_bool_value('ssl_cert_verify', True)
        builder.set_string_value('authentication_method', 'jwt')
        options = builder.get_options()

        if not options['identity_type_filter'] == 'all':
            try:
                options['identity_type_filter'] = parse_identity_type(options['identity_type_filter'])
            except Exception as e:
                raise AssertionException("Error parsing identity_type_filter option: %s" % e)
        self.filter_by_identity_type = options['identity_type_filter']

        server_config = caller_config.get_dict_config('server', True)
        server_builder = config_common.OptionsBuilder(server_config)
        server_builder.set_string_value('host', 'usermanagement.adobe.io')
        server_builder.set_string_value('endpoint', '/v2/usermanagement')
        server_builder.set_string_value('ims_endpoint_jwt', '/ims/exchange/jwt')

        auth_host_key = 'ims_host' if 'ims_host' in server_config else 'auth_host'
        server_builder.set_string_value(auth_host_key, 'ims-na1.adobelogin.com')

        auth_endpoint_key = 'ims_endpoint_jwt' if 'ims_endpoint_jwt' in server_config else 'auth_endpoint'
        auth_endpoint_default = '/ims/exchange/jwt'
        if options['authentication_method'] == 'oauth':
            auth_endpoint_default = '/ims/token/v2'
        server_builder.set_string_value(auth_endpoint_key, auth_endpoint_default)

        server_builder.set_int_value('timeout', 120)
        server_builder.set_int_value('retries', 3)
        options['server'] = server_options = server_builder.get_options()

        enterprise_config = caller_config.get_dict_config('integration')
        integration_builder = config_common.OptionsBuilder(enterprise_config)
        integration_builder.require_string_value('org_id')
        tech_field = 'tech_acct_id' if 'tech_acct_id' in enterprise_config else 'tech_acct'
        integration_builder.set_string_value(tech_field, None)
        options['integration'] = integration_options = integration_builder.get_options()

        if integration_options[tech_field] is None and options['authentication_method'] == 'jwt':
            raise AssertionException(f"'{tech_field}' is required for jwt authentication")

        if integration_options[tech_field] is not None and options['authentication_method'] == 'oauth':
            raise AssertionException(f"'{tech_field}' should not be set for oauth authentication")

        self.logger = logger = user_sync.connector.helper.create_logger(options)
        logger.debug('%s initialized with options: %s', self.name, options)

        self.options = options

        self.org_id = org_id = integration_options['org_id']
        auth = create_umapi_auth(
            self.name,
            enterprise_config,
            org_id,
            integration_options[tech_field],
            server_options[auth_host_key],
            server_options[auth_endpoint_key],
            options['ssl_cert_verify'],
            options['authentication_method'],
            logger,
        )

        # this check must come after we fetch all the settings
        caller_config.report_unused_values(logger)
        # open the connection
        um_endpoint = "https://" + server_options['host'] + server_options['endpoint']
        logger.debug('%s: creating connection for org %s at endpoint %s', self.name, org_id, um_endpoint)

        try:
            self.connection = umapi_client.Connection(
                org_id=org_id,
                auth=auth,
                endpoint=um_endpoint,
                test_mode=False,
                user_agent="user-sync/" + app_version,
                timeout=float(server_options['timeout']),
                max_retries=server_options['retries'] + 1,
                ssl_verify=options['ssl_cert_verify']
            )
        except Exception as e:
            raise AssertionException("Connection to org %s at endpoint %s failed: %s" % (org_id, um_endpoint, e))
        logger.debug('%s: connection established', self.name)
        self.umapi_users = []
        self.user_by_usr_key = {}

    def set_additional_group_filters(self, _):
        pass

    def load_users_and_groups(self, groups, extended_attributes, all_users):
        """
        :type groups: list(str)
        :type extended_attributes: list(str)
        :type all_users: bool
        :rtype (bool, iterable(dict))
        """

        if extended_attributes:
            self.logger.warning("Extended Attributes is not supported")

        # Loading all the groups because UMAPI doesn't support group query. DOH!
        self.logger.info('Loading groups...')
        umapi_groups = [g.lower() for g in self.iter_umapi_groups()]
        self.logger.info('Loading users...')

        # Loading all umapi users based on ID Type first before doing group filtering
        filter_by_identity_type = self.filter_by_identity_type
        self.load_umapi_users(identity_type=filter_by_identity_type)

        grouped_user_records = {}
        for group in groups:
            group_users_count = 0
            if group in umapi_groups:
                grouped_users = self.iter_group_members(group)
                for user_key in grouped_users:
                    if user_key in self.user_by_usr_key:
                        user = self.user_by_usr_key[user_key]
                        user['groups'].append(group)
                        self.user_by_usr_key[user_key] = grouped_user_records[user_key] = user
                        group_users_count = group_users_count + 1
                self.logger.debug('Count of users in group "%s": %d', group, group_users_count)
            else:
                self.logger.warning("No group found for: %s", group)
        if all_users:
            self.logger.debug('Count of users in any groups: %d', len(grouped_user_records))
            self.logger.debug('Count of users not in any groups: %d',
                              len(self.user_by_usr_key) - len(grouped_user_records))
            return self.user_by_usr_key.values()
        else:
            return grouped_user_records.values()

    def convert_user(self, record):

        source_attributes = {}
        user = user_sync.connector.helper.create_blank_user()
        user['uid'] = record['username']
        source_attributes['email'] = user['email'] = email = record['email']
        user_identity_type = record['type']
        try:
            source_attributes['type'] = user['identity_type'] = user_sync.identity_type.parse_identity_type(
                user_identity_type)
        except AssertionException as e:
            self.logger.warning('Skipping user %s: %s', email, e)
            return None

        source_attributes['username'] = user['username'] = record['username']
        source_attributes['domain'] = user['domain'] = record['domain']

        if 'firstname' in record:
            firstname = record['firstname']
        else:
            firstname = None
        source_attributes['firstname'] = user['firstname'] = firstname

        if 'lastname' in record:
            lastname = record['lastname']
        else:
            lastname = None
        source_attributes['lastname'] = user['lastname'] = lastname

        source_attributes['country'] = user['country'] = record['country']

        user['source_attributes'] = source_attributes.copy()

        groups = record.get('groups', [])
        user['member_groups'] = groups

        return user

    def iter_umapi_groups(self):
        try:
            groups = umapi_client.GroupsQuery(self.connection)
            for group in groups:
                yield group['groupName']
        except umapi_client.UnavailableError as e:
            raise AssertionException("Error to query groups from Adobe Console: %s" % e)

    def iter_group_members(self, group):
        umapi_users = self.umapi_users
        members = filter(lambda u: ('groups' in u and group in [g.lower() for g in u['groups']]), umapi_users)
        for member in members:
            user_key = self.generate_user_key(member['type'], member['username'], member['domain'])
            yield user_key

    def load_umapi_users(self, identity_type):
        try:
            u_query = umapi_client.UsersQuery(self.connection)
            umapi_users = u_query.all_results()

            if not identity_type == 'all':
                umapi_users = list(filter(lambda usr: usr['type'] == identity_type, umapi_users))

            self.umapi_users = umapi_users
            for user in umapi_users:
                # Generate unique user key because Username/Email is a bad unique identifier
                user_key = self.generate_user_key(user['type'], user['username'], user['domain'])
                self.user_by_usr_key[user_key] = self.convert_user(user)
        except umapi_client.UnavailableError as e:
            raise AssertionException("Error contacting UMAPI server: %s" % e)

    def generate_user_key(self, identity_type, username, domain):
        return '%s,%s,%s' % (normalize_string(identity_type), normalize_string(username), normalize_string(domain))
