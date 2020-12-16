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

import six
import umapi_client
import user_sync.connector.helper
import user_sync.helper
import user_sync.identity_type
from user_sync.error import AssertionException
from user_sync.version import __version__ as app_version
from user_sync.connector.umapi_util import make_auth_dict
from user_sync.helper import normalize_string
from user_sync.identity_type import parse_identity_type
from user_sync.config import user_sync as config
from user_sync.config import common as config_common


def connector_metadata():
    metadata = {
        'name': AdobeConsoleConnector.name
    }
    return metadata


def connector_initialize(options):
    """
    :type options: dict
    """
    state = AdobeConsoleConnector(options)
    return state


def connector_load_users_and_groups(state, groups=None, extended_attributes=None, all_users=True):
    """
    :type state: OktaDirectoryConnector
    :type groups: list(str)
    :type extended_attributes: list(str)
    :type all_users: bool
    :rtype (bool, iterable(dict))
    """

    return state.load_users_and_groups(groups or [], extended_attributes or [], all_users)


class AdobeConsoleConnector(object):
    name = 'adobe_console'

    def __init__(self, caller_options):

        caller_config = config_common.DictConfig('<%s configuration>' % self.name, caller_options)
        builder = config_common.OptionsBuilder(caller_config)
        # Let just ignore this
        builder.set_string_value('user_identity_type', None)
        builder.set_string_value('identity_type_filter', 'all')
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
        server_builder.set_string_value('ims_host', 'ims-na1.adobelogin.com')
        server_builder.set_string_value('ims_endpoint_jwt', '/ims/exchange/jwt')
        server_builder.set_int_value('timeout', 120)
        server_builder.set_int_value('retries', 3)
        options['server'] = server_options = server_builder.get_options()

        enterprise_config = caller_config.get_dict_config('integration')
        integration_builder = config_common.OptionsBuilder(enterprise_config)
        integration_builder.require_string_value('org_id')
        tech_field = 'tech_acct_id' if 'tech_acct_id' in enterprise_config else 'tech_acct'
        integration_builder.require_string_value(tech_field)
        options['integration'] = integration_options = integration_builder.get_options()

        self.logger = logger = user_sync.connector.helper.create_logger(options)
        logger.debug('%s initialized with options: %s', self.name, options)

        self.options = options

        ims_host = server_options['ims_host']
        self.org_id = org_id = integration_options['org_id']
        auth_dict = make_auth_dict(self.name, enterprise_config, org_id, integration_options[tech_field], logger)

        # this check must come after we fetch all the settings
        caller_config.report_unused_values(logger)
        # open the connection
        um_endpoint = "https://" + server_options['host'] + server_options['endpoint']
        logger.debug('%s: creating connection for org %s at endpoint %s', self.name, org_id, um_endpoint)

        try:
            self.connection = umapi_client.Connection(
                org_id=org_id,
                auth_dict=auth_dict,
                ims_host=ims_host,
                ims_endpoint_jwt=server_options['ims_endpoint_jwt'],
                user_management_endpoint=um_endpoint,
                test_mode=False,
                user_agent="user-sync/" + app_version,
                logger=self.logger,
                timeout_seconds=float(server_options['timeout']),
                retry_max_attempts=server_options['retries'] + 1,
            )
        except Exception as e:
            raise AssertionException("Connection to org %s at endpoint %s failed: %s" % (org_id, um_endpoint, e))
        logger.debug('%s: connection established', self.name)
        self.umapi_users = []
        self.user_by_usr_key = {}

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
        umapi_groups = list(self.iter_umapi_groups())
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
            return six.itervalues(self.user_by_usr_key)
        else:
            return six.itervalues(grouped_user_records)

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
        members = filter(lambda u: ('groups' in u and group in u['groups']), umapi_users)
        for member in members:
            user_key = self.generate_user_key(member['type'], member['username'], member['domain'])
            yield (user_key)

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
