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

import json
import logging
# import helper

import jwt
import six
import umapi_client
from Crypto.PublicKey import RSA

import user_sync.connector.helper
import user_sync.config
import user_sync.helper
import user_sync.identity_type
from user_sync.error import AssertionException
from user_sync.version import __version__ as app_version

try:
    from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
    jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))
except:
    pass


class UmapiConnector(object):
    def __init__(self, name, caller_options):
        """
        :type name: str
        :type caller_options: dict
        """
        self.name = 'umapi' + name
        caller_config = user_sync.config.DictConfig(self.name + ' configuration', caller_options)
        builder = user_sync.config.OptionsBuilder(caller_config)
        builder.set_string_value('logger_name', self.name)
        builder.set_bool_value('test_mode', False)
        options = builder.get_options()

        server_config = caller_config.get_dict_config('server', True)
        server_builder = user_sync.config.OptionsBuilder(server_config)
        server_builder.set_string_value('host', 'usermanagement.adobe.io')
        server_builder.set_string_value('endpoint', '/v2/usermanagement')
        server_builder.set_string_value('ims_host', 'ims-na1.adobelogin.com')
        server_builder.set_string_value('ims_endpoint_jwt', '/ims/exchange/jwt')
        server_builder.set_int_value('timeout', 120)
        server_builder.set_int_value('retries', 3)
        options['server'] = server_options = server_builder.get_options()

        enterprise_config = caller_config.get_dict_config('enterprise')
        enterprise_builder = user_sync.config.OptionsBuilder(enterprise_config)
        enterprise_builder.require_string_value('org_id')
        enterprise_builder.require_string_value('tech_acct')
        options['enterprise'] = enterprise_options = enterprise_builder.get_options()
        self.options = options
        self.logger = logger = user_sync.connector.helper.create_logger(options)
        if server_config:
            server_config.report_unused_values(logger)
        logger.debug('UMAPI initialized with options: %s', options)

        ims_host = server_options['ims_host']
        self.org_id = org_id = enterprise_options['org_id']
        auth_dict = {
            'org_id': org_id,
            'tech_acct_id': enterprise_options['tech_acct'],
            'api_key': enterprise_config.get_credential('api_key', org_id),
            'client_secret': enterprise_config.get_credential('client_secret', org_id),
        }
        # get the private key
        key_path = enterprise_config.get_string('priv_key_path', True)
        if key_path:
            data_setting = enterprise_config.has_credential('priv_key_data')
            if data_setting:
                raise AssertionException('%s: cannot specify both "priv_key_path" and "%s"' %
                                         (enterprise_config.get_full_scope(), data_setting))
            logger.debug('%s: reading private key data from file %s', self.name, key_path)
            try:
                with open(key_path, 'r') as f:
                    key_data = f.read()
            except IOError as e:
                raise AssertionException('%s: cannot read file "%s": %s' %
                                         (enterprise_config.get_full_scope(), key_path, e))
        else:
            key_data = enterprise_config.get_credential('priv_key_data', org_id)
        # decrypt the private key, if needed
        passphrase = enterprise_config.get_credential('priv_key_pass', org_id, True)
        if passphrase:
            try:
                key_data = str(RSA.importKey(key_data, passphrase=passphrase).exportKey().decode('ascii'))
            except (ValueError, IndexError, TypeError) as e:
                raise AssertionException('%s: Error decrypting private key, either the password is wrong or: %s' %
                                         (enterprise_config.get_full_scope(), e))
        auth_dict['private_key_data'] = key_data
        # this check must come after we fetch all the settings
        enterprise_config.report_unused_values(logger)
        # open the connection
        um_endpoint = "https://" + server_options['host'] + server_options['endpoint']
        logger.debug('%s: creating connection for org %s at endpoint %s', self.name, org_id, um_endpoint)
        try:
            self.connection = connection = umapi_client.Connection(
                org_id=org_id,
                auth_dict=auth_dict,
                ims_host=ims_host,
                ims_endpoint_jwt=server_options['ims_endpoint_jwt'],
                user_management_endpoint=um_endpoint,
                test_mode=options['test_mode'],
                user_agent="user-sync/" + app_version,
                logger=self.logger,
                timeout_seconds=float(server_options['timeout']),
                retry_max_attempts=server_options['retries'] + 1,
            )
        except Exception as e:
            raise AssertionException("Connection to org %s at endpoint %s failed: %s" % (org_id, um_endpoint, e))
        logger.debug('%s: connection established', self.name)
        # wrap the connection in an action manager
        self.action_manager = ActionManager(connection, org_id, logger)

    def get_users(self):
        return list(self.iter_users())

    def iter_users(self):
        users = {}
        try:
            for u in umapi_client.UsersQuery(self.connection):
                email = u['email']
                if not (email in users):
                    users[email] = u
                    yield u
        except umapi_client.UnavailableError as e:
            raise AssertionException("Error contacting UMAPI server: %s" % e)

    def get_action_manager(self):
        return self.action_manager

    def send_commands(self, commands, callback=None):
        """
        :type commands: Commands
        :type callback: callable(dict)
        """
        if len(commands) > 0:
            action_manager = self.get_action_manager()
            action = action_manager.create_action(commands)
            action_manager.add_action(action, callback)


class Commands(object):
    def __init__(self, identity_type=None, email=None, username=None, domain=None):
        """
        :type identity_type: str
        :type email: str
        :type username: str
        :type domain: str
        """
        self.identity_type = identity_type
        self.email = email
        self.username = username
        self.domain = domain
        self.do_list = []

    def update_user(self, attributes):
        """
        :type attributes: dict
        """
        if attributes is not None and len(attributes) > 0:
            params = self.convert_user_attributes_to_params(attributes)
            self.do_list.append(('update', params))

    def add_groups(self, groups_to_add):
        """
        :type groups_to_add: set(str)
        """
        if groups_to_add is not None and len(groups_to_add) > 0:
            params = {
                "groups": groups_to_add
            }
            self.do_list.append(('add_to_groups', params))

    def remove_all_groups(self):
        self.do_list.append(('remove_from_groups', {'all_groups': True}))

    def remove_groups(self, groups_to_remove):
        """
        :type groups_to_remove: set(str)
        """
        if groups_to_remove is not None and len(groups_to_remove) > 0:
            params = {
                'groups': groups_to_remove
            }
            self.do_list.append(('remove_from_groups', params))

    def add_user(self, attributes):
        """
        :type attributes: dict
        """
        params = self.convert_user_attributes_to_params(attributes)

        on_conflict_value = None
        option = params.pop('option', None)
        if option == "updateIfAlreadyExists":
            on_conflict_value = umapi_client.IfAlreadyExistsOptions.updateIfAlreadyExists
        elif option == "ignoreIfAlreadyExists":
            on_conflict_value = umapi_client.IfAlreadyExistsOptions.ignoreIfAlreadyExists
        if on_conflict_value is not None:
            params['on_conflict'] = on_conflict_value

        self.do_list.append(('create', params))

    def remove_from_org(self, delete_account):
        """
        Removes a user from the organization. If delete_account is set, it
        will delete the user on the Adobe side as well.
        :type delete_account: bool
        """
        params = {
            "delete_account": True if delete_account else False
        }
        self.do_list.append(('remove_from_organization', params))

    def __len__(self):
        return len(self.do_list)

    def convert_user_attributes_to_params(self, attributes):
        params = {}
        for key, value in six.iteritems(attributes):
            if key == 'firstname':
                key = 'first_name'
            elif key == 'lastname':
                key = 'last_name'
            params[key] = value
        return params


class ActionManager(object):
    next_request_id = 1

    def __init__(self, connection, org_id, logger):
        """
        :type connection: umapi_client.Connection
        :type org_id: str
        :type logger: logging.Logger
        """
        self.action_count = 0
        self.error_count = 0
        self.items = []
        self.connection = connection
        self.org_id = org_id
        self.logger = logger.getChild('action')

    def get_statistics(self):
        """Return the count of actions sent so far, and how many had errors."""
        return self.action_count, self.error_count

    def get_next_request_id(self):
        request_id = 'action_%d' % ActionManager.next_request_id
        ActionManager.next_request_id += 1
        return request_id

    def create_action(self, commands):
        identity_type = commands.identity_type
        email = commands.email
        username = commands.username
        domain = commands.domain

        if username.find('@') > 0:
            if email is None:
                email = username
            if identity_type is None:
                identity_type = (user_sync.identity_type.FEDERATED_IDENTITY_TYPE
                                 if username != user_sync.helper.normalize_string(email)
                                 else user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE)
        elif identity_type is None:
            identity_type = user_sync.identity_type.FEDERATED_IDENTITY_TYPE
        try:
            umapi_identity_type = umapi_client.IdentityTypes[identity_type]
            action = umapi_client.UserAction(umapi_identity_type, email, username, domain,
                                             requestID=self.get_next_request_id())
        except ValueError as e:
            raise AssertionException("Error creating umapi Action: %s" % e)
        for command in commands.do_list:
            command_name, command_param = command
            command_function = getattr(action, command_name)
            command_function(**command_param)
        return action

    def add_action(self, action, callback=None):
        """
        :type action: umapi_client.UserAction
        :type callback: callable(umapi_client.UserAction, bool, dict)
        """
        item = {
            'action': action,
            'callback': callback
        }
        self.items.append(item)
        self.action_count += 1
        self.logger.debug('Added action: %s', json.dumps(action.wire_dict()))
        self._execute_action(action)

    def has_work(self):
        return len(self.items) > 0

    def _execute_action(self, action):
        """
        :type action: umapi_client.UserAction
        """
        try:
            _, sent, _ = self.connection.execute_single(action)
        except umapi_client.BatchError as e:
            self.process_sent_items(e.statistics[1], e)
        except umapi_client.UnavailableError as e:
            raise AssertionException("Error contacting UMAPI server: %s" % e)
        else:
            self.process_sent_items(sent)

    def flush(self):
        try:
            _, sent, _ = self.connection.execute_queued()
        except umapi_client.BatchError as e:
            self.process_sent_items(e.statistics[1], e)
        except umapi_client.UnavailableError as e:
            raise AssertionException("Error contacting UMAPI server: %s" % e)
        else:
            self.process_sent_items(sent)

    def process_sent_items(self, total_sent, batch_error=None):
        """
        Note items as sent, log any processing errors, and invoke any callbacks
        :param total_sent: number of sent items from queue, must be >= 0
        :param batch_error: exception for a batch-level error that affected all items, if there was one
        :return: 
        """
        # update queue
        sent_items, self.items = self.items[:total_sent], self.items[total_sent:]

        # collect sent actions, their errors, their callbacks
        details = [(item['action'], item['action'].execution_errors(), item['callback']) for item in sent_items]

        # log errors
        if batch_error:
            request_ids = str([action.frame.get("requestID") for action, _, _ in details])
            self.logger.critical("Unexpected response! Sent actions %s may have failed: %s", request_ids, batch_error)
            self.error_count += total_sent
        else:
            for action, errors, _ in details:
                if errors:
                    self.error_count += 1
                    for error in errors:
                        self.logger.error('Error in requestID: %s (User: %s, Command: %s): code: "%s" message: "%s"',
                                          action.frame.get("requestID"),
                                          error.get("target", "<Unknown>"), error.get("command", "<Unknown>"),
                                          error.get('errorCode', "<None>"), error.get('message', "<None>"))
        # invoke callbacks
        for action, errors, callback in details:
            if callable(callback):
                callback({
                    "action": action,
                    "is_success": not batch_error and not errors,
                    "errors": [batch_error] if batch_error else errors
                })
