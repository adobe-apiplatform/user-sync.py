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

import six
import string

import ldap.controls.libldap

import user_sync.config
import user_sync.connector.helper
import user_sync.error
import user_sync.identity_type
from user_sync.error import AssertionException


def connector_metadata():
    metadata = {
        'name': LDAPDirectoryConnector.name
    }
    return metadata


def connector_initialize(options):
    """
    :type options: dict
    """
    connector = LDAPDirectoryConnector(options)
    return connector


def connector_load_users_and_groups(state, groups=None, extended_attributes=None, all_users=True):
    """
    :type state: LDAPDirectoryConnector
    :type groups: Optional(list(str))
    :type extended_attributes: Optional(list(str))
    :type all_users: bool
    :rtype (bool, iterable(dict))
    """
    return state.load_users_and_groups(groups or [], extended_attributes or [], all_users)


class LDAPDirectoryConnector(object):
    name = 'ldap'

    expected_result_types = [ldap.RES_SEARCH_RESULT, ldap.RES_SEARCH_ENTRY]

    def __init__(self, caller_options):
        caller_config = user_sync.config.DictConfig('%s configuration' % self.name, caller_options)
        builder = user_sync.config.OptionsBuilder(caller_config)
        builder.set_string_value('group_filter_format', six.text_type(
            '(&(|(objectCategory=group)(objectClass=groupOfNames)(objectClass=posixGroup))(cn={group}))'))
        builder.set_string_value('all_users_filter', six.text_type(
            '(&(objectClass=user)(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'))
        builder.set_string_value('group_member_filter_format', six.text_type(
            '(memberOf={group_dn})'))
        builder.set_bool_value('require_tls_cert', False)
        builder.set_string_value('string_encoding', 'utf8')
        builder.set_string_value('user_identity_type_format', None)
        builder.set_string_value('user_email_format', six.text_type('{mail}'))
        builder.set_string_value('user_username_format', None)
        builder.set_string_value('user_domain_format', None)
        builder.set_string_value('user_identity_type', None)
        builder.set_int_value('search_page_size', 200)
        builder.set_string_value('logger_name', LDAPDirectoryConnector.name)
        host = builder.require_string_value('host')
        username = builder.require_string_value('username')
        builder.require_string_value('base_dn')
        options = builder.get_options()
        self.options = options
        self.logger = logger = user_sync.connector.helper.create_logger(options)
        logger.debug('%s initialized with options: %s', self.name, options)

        LDAPValueFormatter.encoding = options['string_encoding']
        self.user_identity_type = user_sync.identity_type.parse_identity_type(options['user_identity_type'])
        self.user_identity_type_formatter = LDAPValueFormatter(options['user_identity_type_format'])
        self.user_email_formatter = LDAPValueFormatter(options['user_email_format'])
        self.user_username_formatter = LDAPValueFormatter(options['user_username_format'])
        self.user_domain_formatter = LDAPValueFormatter(options['user_domain_format'])

        password = caller_config.get_credential('password', options['username'])
        # this check must come after we get the password value
        caller_config.report_unused_values(logger)

        logger.debug('Connecting to: %s using username: %s', host, username)
        if not options['require_tls_cert']:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        try:
            # Be careful in Py2!!  We are setting bytes_mode = False, so we must give all attribute names
            # and other protocol-defined strings (such as username) as Unicode.  But the PyYAML parser
            # will always return ascii strings as str type (rather than Unicode).  So we must be careful
            # to upconvert all parameter strings to unicode when passing them in.
            connection = ldap.initialize(host, bytes_mode=False)
            connection.protocol_version = ldap.VERSION3
            connection.set_option(ldap.OPT_REFERRALS, 0)
            connection.simple_bind_s(six.text_type(username), six.text_type(password))
        except Exception as e:
            raise AssertionException('LDAP connection failure: %s' % e)
        self.connection = connection
        logger.debug('Connected')
        self.user_by_dn = {}

    def load_users_and_groups(self, groups, extended_attributes, all_users):
        """
        :type groups: list(str)
        :type extended_attributes: list(str)
        :type all_users: bool
        :rtype (bool, iterable(dict))
        """
        options = self.options
        all_users_filter = six.text_type(options['all_users_filter'])
        group_member_filter_format = six.text_type(options['group_member_filter_format'])

        # for each group that's required, do one search for the users of that group
        for group in groups:
            group_dn = self.find_ldap_group_dn(group)
            if not group_dn:
                self.logger.warning("No group found for: %s", group)
                continue
            group_member_subfilter = self.format_ldap_query_string(group_member_filter_format, group_dn=group_dn)
            if not group_member_subfilter.startswith('('):
                group_member_subfilter = six.text_type('(') + group_member_subfilter + six.text_type(')')
            user_subfilter = all_users_filter
            if not user_subfilter.startswith('('):
                user_subfilter = six.text_type('(') + user_subfilter + six.text_type(')')
            group_user_filter = six.text_type('(&') + group_member_subfilter + user_subfilter + six.text_type(')')
            group_users = 0
            try:
                for user_dn, user in self.iter_users(group_user_filter, extended_attributes):
                    user['groups'].append(group)
                    group_users += 1
                self.logger.debug('Count of users in group "%s": %d', group, group_users)
            except Exception as e:
                raise AssertionException('Unexpected LDAP failure reading group members: %s' % e)

        # if all users are requested, do an additional search for all of them
        if all_users:
            ungrouped_users = 0
            grouped_users = 0
            try:
                for user_dn, user in self.iter_users(all_users_filter, extended_attributes):
                    if not user['groups']:
                        ungrouped_users += 1
                    else:
                        grouped_users += 1
                if groups:
                    self.logger.debug('Count of users in any groups: %d', grouped_users)
                    self.logger.debug('Count of users not in any groups: %d', ungrouped_users)
            except Exception as e:
                raise AssertionException('Unexpected LDAP failure reading all users: %s' % e)

        self.logger.debug('Total users loaded: %d', len(self.user_by_dn))
        return six.itervalues(self.user_by_dn)

    def find_ldap_group_dn(self, group):
        """
        :type group: str
        :rtype str
        """
        connection = self.connection
        options = self.options
        base_dn = six.text_type(options['base_dn'])
        group_filter_format = six.text_type(options['group_filter_format'])
        try:
            res = connection.search_s(base_dn, ldap.SCOPE_SUBTREE,
                                      filterstr=self.format_ldap_query_string(group_filter_format, group=group), attrsonly=1)
        except Exception as e:
            raise AssertionException('Unexpected LDAP failure reading group info: %s' % e)
        group_dn = None
        for current_tuple in res:
            if current_tuple[0]:
                if group_dn:
                    raise AssertionException("Multiple LDAP groups found for: %s" % group)
                group_dn = current_tuple[0]
        return group_dn

    def iter_users(self, users_filter, extended_attributes):
        options = self.options
        base_dn = six.text_type(options['base_dn'])

        user_attribute_names = [six.text_type('givenName'), six.text_type('sn'), six.text_type('c')]
        user_attribute_names.extend(self.user_identity_type_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_email_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_username_formatter.get_attribute_names())
        user_attribute_names.extend(self.user_domain_formatter.get_attribute_names())

        extended_attributes = [six.text_type(attr) for attr in extended_attributes]
        extended_attributes = list(set(extended_attributes) - set(user_attribute_names))
        user_attribute_names.extend(extended_attributes)

        result_iter = self.iter_search_result(base_dn, ldap.SCOPE_SUBTREE, users_filter, user_attribute_names)
        for dn, record in result_iter:
            if dn is None:
                continue
            if dn in self.user_by_dn:
                yield (dn, self.user_by_dn[dn])
                continue

            email, last_attribute_name = self.user_email_formatter.generate_value(record)
            email = email.strip() if email else None
            if not email:
                if last_attribute_name is not None:
                    self.logger.warning('Skipping user with dn %s: empty email attribute (%s)', dn, last_attribute_name)
                continue

            source_attributes = {}

            user = user_sync.connector.helper.create_blank_user()
            source_attributes['email'] = email
            user['email'] = email

            identity_type, last_attribute_name = self.user_identity_type_formatter.generate_value(record)
            if last_attribute_name and not identity_type:
                self.logger.warning('No identity_type attribute (%s) for user with dn: %s, defaulting to %s',
                                    last_attribute_name, dn, self.user_identity_type)
            source_attributes['identity_type'] = identity_type
            if not identity_type:
                user['identity_type'] = self.user_identity_type
            else:
                try:
                    user['identity_type'] = user_sync.identity_type.parse_identity_type(identity_type)
                except AssertionException as e:
                    self.logger.warning('Skipping user with dn %s: %s', dn, e)
                    continue

            username, last_attribute_name = self.user_username_formatter.generate_value(record)
            username = username.strip() if username else None
            source_attributes['username'] = username
            if username:
                user['username'] = username
            else:
                if last_attribute_name:
                    self.logger.warning('No username attribute (%s) for user with dn: %s, default to email (%s)',
                                        last_attribute_name, dn, email)
                user['username'] = email

            domain, last_attribute_name = self.user_domain_formatter.generate_value(record)
            domain = domain.strip() if domain else None
            source_attributes['domain'] = domain
            if domain:
                user['domain'] = domain
            elif username != email:
                user['domain'] = email[email.find('@') + 1:]
            elif last_attribute_name:
                self.logger.warning('No domain attribute (%s) for user with dn: %s', last_attribute_name, dn)

            given_name_value = LDAPValueFormatter.get_attribute_value(record, six.text_type('givenName'))
            source_attributes['givenName'] = given_name_value
            if given_name_value is not None:
                user['firstname'] = given_name_value
            sn_value = LDAPValueFormatter.get_attribute_value(record, six.text_type('sn'))
            source_attributes['sn'] = sn_value
            if sn_value is not None:
                user['lastname'] = sn_value
            c_value = LDAPValueFormatter.get_attribute_value(record, six.text_type('c'))
            source_attributes['c'] = c_value
            if c_value is not None:
                user['country'] = c_value

            if extended_attributes is not None:
                for extended_attribute in extended_attributes:
                    extended_attribute_value = LDAPValueFormatter.get_attribute_value(record, extended_attribute)
                    source_attributes[extended_attribute] = extended_attribute_value

            user['source_attributes'] = source_attributes.copy()
            if 'groups' not in user:
                user['groups'] = []
            self.user_by_dn[dn] = user

            yield (dn, user)

    def iter_search_result(self, base_dn, scope, filter_string, attributes):
        """
        type: filter_string: str
        type: attributes: list(str)
        """
        connection = self.connection
        search_page_size = self.options['search_page_size']

        lc = ldap.controls.libldap.SimplePagedResultsControl(True, size=search_page_size, cookie='')

        msgid = None
        try:
            has_next_page = True
            while has_next_page:
                response_data = None
                result_type = None
                if msgid is not None:
                    result_type, response_data, _rmsgid, serverctrls = connection.result3(msgid)
                    msgid = None
                    pctrls = [c for c in serverctrls
                              if c.controlType == ldap.controls.libldap.SimplePagedResultsControl.controlType]
                    if not pctrls:
                        self.logger.warn('Server ignored RFC 2696 control.')
                        has_next_page = False
                    else:
                        lc.cookie = cookie = pctrls[0].cookie
                        if not cookie:
                            has_next_page = False
                if has_next_page:
                    msgid = connection.search_ext(base_dn, scope,
                                                  filterstr=filter_string, attrlist=attributes, serverctrls=[lc])
                if result_type in self.expected_result_types and (response_data is not None):
                    for item in response_data:
                        yield item
        except GeneratorExit:
            if msgid is not None:
                connection.abandon(msgid)
            raise

    @staticmethod
    def format_ldap_query_string(query, **kwargs):
        """
        To be used with any string that will be injected into a LDAP query - this escapes a few special characters that
        may appear in DNs, group names, etc.
        :param query:
        :param kwargs:
        :return:
        """
        escape_chars = six.text_type('*()\\&|<>~!:')
        escaped_args = {}
        # kwargs is a dict that would normally be passed to string.format
        for k, v in six.iteritems(kwargs):
            # LDAP special characters are escaped in the general format '\' + hex(char)
            # we need to run through the string char by char and if the char exists in
            # the escape_char list, get the ord of it (decimal ascii value), convert it to hex, and
            # replace the '0x' with '\'
            escaped_list = []
            for c in v:
                if c in escape_chars:
                    replace = six.text_type(hex(ord(c))).replace('0x', '\\')
                    escaped_list.append(replace)
                else:
                    escaped_list.append(c)
            escaped_args[k] = six.text_type('').join(escaped_list)
        return query.format(**escaped_args)


class LDAPValueFormatter(object):
    encoding = 'utf8'

    def __init__(self, string_format):
        """
        The format string must be a unicode or ascii string: see notes above about being careful in Py2!
        """
        if string_format is None:
            attribute_names = []
        else:
            string_format = six.text_type(string_format)    # force unicode so attribute values are unicode
            formatter = string.Formatter()
            attribute_names = [six.text_type(item[1]) for item in formatter.parse(string_format) if item[1]]
        self.string_format = string_format
        self.attribute_names = attribute_names

    def get_attribute_names(self):
        """
        :rtype list(str)
        """
        return self.attribute_names

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
                value = self.get_attribute_value(record, attribute_name, first_only=True)
                if value is None:
                    values = None
                    break
                values[attribute_name] = value
            if values is not None:
                result = self.string_format.format(**values)
        return result, attribute_name

    @classmethod
    def get_attribute_value(cls, attributes, attribute_name, first_only=False):
        """
        The attribute value type must be decodable (str in py2, bytes in py3)
        :type attributes: dict
        :type attribute_name: unicode
        :type first_only: bool
        """
        attribute_values = attributes.get(attribute_name)
        if attribute_values:
            try:
                if first_only or len(attribute_values) == 1:
                    return attribute_values[0].decode(cls.encoding)
                else:
                    return [val.decode(cls.encoding) for val in attribute_values]
            except UnicodeError as e:
                raise AssertionException("Encoding error in value of attribute '%s': %s" % (attribute_name, e))
        return None
