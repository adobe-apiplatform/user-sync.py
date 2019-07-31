import six
import ldap3

import user_sync.rules
import user_sync.connector.directory
import user_sync.sign_sync.connections.sign_connection

from user_sync.error import AssertionException

class Synchronize:

    def __init__(self, logger, config_loader, connector):

        # Create process, api, and error loggers for Sign Sync
        self.logs = logger
        self.config_loader = config_loader
        self.connector = connector

        # Instantiate Sign object
        self.sign_obj = user_sync.sign_sync.connections.sign_connection.Sign(self.logs)

        # Get LDAP connector and connect to it
        self.ldap_connector = self.get_ldap_connectors()
        self.connection = self.ldap_connection(self.ldap_connector)

        # Get access to UMAPI connectors
        self.umapi_connectors = self.get_umapi_connectors()
        self.umapi_primary_connector = self.umapi_connectors.get_primary_connector()

        self.run()

    def run(self):

        self.logs.info('------------------------------- Starting Sign Sync -------------------------------')

        # Get Sign config & validate integration key
        sign_config = self.sign_obj.get_config_dict()
        self.sign_obj.validate_integration_key(sign_config['header'], sign_config['url'])

        # Get a list of UMAPI users
        umapi_user_list =  self.umapi_primary_connector.get_users()

        # Group Creation and processing users
        sign_user_list = self.get_user_sign_id(umapi_user_list, sign_config)
        umapi_group_list = self.parse_groups(sign_config, sign_user_list)
        self.sign_obj.create_sign_group(umapi_group_list, sign_config)
        self.process_user(sign_user_list, sign_config)

        self.logs.info('------------------------------- Ending Sign Sync ---------------------------------')

    def get_umapi_connectors(self):
        """
        This function will setup and retrieve the UMAPI connector.
        :return: UmapiConnectors
        """

        primary_umapi_config, secondary_umapi_configs = self.config_loader.get_umapi_options()
        primary_name = '.primary' if secondary_umapi_configs else ''
        umapi_primary_connector = self.connector.umapi.UmapiConnector(primary_name, primary_umapi_config)
        umapi_other_connectors = {}
        for secondary_umapi_name, secondary_config in six.iteritems(secondary_umapi_configs):
            umapi_secondary_conector = self.connector.umapi.UmapiConnector(".secondary.%s" % secondary_umapi_name,
                                                                                secondary_config)
            umapi_other_connectors[secondary_umapi_name] = umapi_secondary_conector
        umapi_connectors = user_sync.rules.UmapiConnectors(umapi_primary_connector, umapi_other_connectors)

        return umapi_connectors

    def get_ldap_connectors(self):
        """
        This function will get and retrieve the ldap connector.
        :return: DirectoryConnector
        """

        rule_config = self.config_loader.get_rule_options()
        directory_connector = None
        directory_connector_options = None
        directory_connector_module_name = self.config_loader.get_directory_connector_module_name()
        if directory_connector_module_name is not None:
            directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])
            directory_connector = user_sync.connector.directory.DirectoryConnector(directory_connector_module)
            directory_connector_options = self.config_loader.get_directory_connector_options(directory_connector.name)

        self.config_loader.check_unused_config_keys()

        if directory_connector is not None and directory_connector_options is not None:
            # specify the default user_identity_type if it's not already specified in the options
            if 'user_identity_type' not in directory_connector_options:
                directory_connector_options['user_identity_type'] = rule_config['new_account_type']
            directory_connector.initialize(directory_connector_options)

        return directory_connector

    def ldap_connection(self, connector):
        """
        This function establish a connection with the LDAP
        :param connector: LDAP connector
        :return: ldap.conn
        """

        directory_option = self.config_loader.get_directory_connector_options(connector.name)
        host = directory_option['host']
        username = directory_option['username']
        password = directory_option['password']
        auth = {'authentication': ldap3.SIMPLE, 'user': six.text_type(username),
                'password': six.text_type(password)}

        try:
            server = ldap3.Server(host=host, allowed_referral_hosts=True)
            connection = ldap3.Connection(server, auto_bind=True, read_only=True, **auth)
        except Exception as e:
            raise AssertionException('LDAP connection failure: %s' % e)

        return connection

    def get_extra_ldap_attr(self, connector, name):
        directory_option = self.config_loader.get_directory_connector_options(connector.name)
        base_dn = directory_option['base_dn']
        self.connection.search(base_dn, "(CN={})".format(name), ldap3.SUBTREE)
        user_data = self.connection.entries
        temp_user_info = dict()

        if 'company' in user_data:
            temp_user_info['company'] = user_data['company'][0].decode("utf-8")
        if 'title' in user_data:
            temp_user_info['title'] = user_data['title'][0].decode("utf-8")

        return temp_user_info

    def process_user(self, user_list, sign_config):
        """
        This function will process each user and assign them to their Sign groups
        :param user_list:
        :param sign_config:
        :return:
        """

        # Iterate through each user from the user list
        for user in user_list:
            # Skip main account because we don't want to change anything
            if user['email'] == sign_config['email']:
                continue
            name = "{} {}".format(user['firstname'], user['lastname'])
            filter_group_list = self.filter_group(sign_config, user['groups'], False)

            # If the user is not in a group we will assign them to a default group
            if len(filter_group_list) == 0:
                default_group_id = sign_config['group'].get('Default Group')
                temp_payload = self.get_user_info(user, sign_config, default_group_id)
                temp_payload.update(self.get_extra_ldap_attr(self.ldap_connector, name))
                self.sign_obj.add_user_to_sign_group(sign_config, user['id'], default_group_id, temp_payload)

            # Sort the groups and assign the user to first group
            # Sign doesn't support multi group assignment at this time
            else:
                for group in sorted(user['groups']):
                    group_id = sign_config['group'].get(group)

                    if group_id is not None and group not in sign_config['condition']['ignore_groups']:
                        temp_payload = self.get_user_info(user, sign_config, group_id, group)
                        temp_payload.update(self.get_extra_ldap_attr(self.ldap_connector, name))
                        self.sign_obj.add_user_to_sign_group(sign_config, user['id'], group_id, temp_payload)
                        break

    def get_user_sign_id(self, user_list, sign_config):
        """
        This function will grab all User ID in Adobe Sign for the umapi list
        :param user_list: list[]
        :param sign_config: dict()
        :return: list[]
        """

        temp_user_list = list()

        # Iterate through the user list and convert emails with + to %2B
        for user in user_list:
            user_email = user['email']

            #TODO decode special charters
            if '+' in user_email:
                user_email = user_email.replace('+', '%2B')

            # Check to see if user is assigned to a group that contains the product profile name
            if 'groups' in user and any(x in sign_config['condition']['product_group'] for x in user['groups']):
                sign_user_id = self.sign_obj.check_user_existence_in_sign(sign_config, user_email)

                if sign_user_id is not None:
                    user['id'] = sign_user_id
                    temp_user_list.append(user)

        return temp_user_list

    def parse_groups(self, sign_config, user_list):
        """
        This function will compare Admin Console groups and users with Adobe Sign Groups/Users and perform movement of
        users.
        :param sign_config: dict()
        :param user_list: list[]
        :return: list[]
        """

        temp_group_list = list()

        for user in user_list:
            temp_group_list = temp_group_list + user['groups']

        temp_group_list = set(temp_group_list)
        temp_group_list = self.filter_group(sign_config, temp_group_list, True)
        temp_group_list = [group for group in temp_group_list if group not in sign_config['group']]

        return temp_group_list

    def get_user_info(self, user_info, sign_config, group_id, group=None):
        """
        Retrieve user's information
        :param user_info: dict()
        :param sign_config: dict()
        :param group_id: str
        :param group: list[]
        :return: dict()
        """

        privileges = self.check_umapi_privileges(group, user_info, sign_config['condition'])
        data = self.update_user_info(user_info, group_id, privileges, sign_config['connector'])

        return data

    @staticmethod
    def check_umapi_privileges(group, umapi_user_info, sign_condition):
        """
        This function will look through the configuration settings and give access privileges access to each user.
        :param group: list[]
        :param umapi_user_info: dict()
        :param sign_condition: dict()
        :return:
        """

        # Set initial flags
        privileges = ["NORMAL_USER"]
        acc_admin_flag = False
        ignore_group_flag = False
        group_admin_flag = False

        if group is not None:

            for user_group in umapi_user_info['groups']:

                # Check to see if privileges match the ones set in the configuration file
                for priv in sign_condition['account_admin_groups']:
                    if priv in user_group:
                        acc_admin_flag = True

                # Check to see if any groups is part of the ignore admin groups in the configuration file
                for ignore in sign_condition['ignore_admin_groups']:
                    if ignore in group:
                        ignore_group_flag = True

                # Check to see if groups are part of an admin group
                if len(user_group) >= 7 and '_admin_' in user_group[:7]:
                    if user_group[7:] == group:
                        group_admin_flag = True

            # Determine the correct privileges to assign to the user
            if acc_admin_flag and group_admin_flag and ignore_group_flag:
                privileges = ['GROUP_ADMIN']
            elif acc_admin_flag and group_admin_flag and not ignore_group_flag:
                privileges = ["ACCOUNT_ADMIN", "GROUP_ADMIN"]
            elif not acc_admin_flag and group_admin_flag and ignore_group_flag:
                privileges = ["GROUP_ADMIN"]
            elif acc_admin_flag and not group_admin_flag and not ignore_group_flag:
                privileges = ["ACCOUNT_ADMIN"]
            elif not acc_admin_flag and group_admin_flag and not ignore_group_flag:
                privileges = ["GROUP_ADMIN"]
            else:
                privileges = ["NORMAL_USER"]

        else:
            filter_words = ['_org_admin', '_PRODUCT_ADMIN', '_deployment_admin', '_support_admin']
            product_profile = set(sign_condition['product_group'])
            temp_list = umapi_user_info['groups']
            temp_list = list(filter(lambda x: x not in product_profile, temp_list))
            temp_group_list = [group for group in temp_list if any(word in group for word in filter_words)]

            if len(temp_group_list) > 0:
                privileges = ["ACCOUNT_ADMIN"]

        return privileges

    @staticmethod
    def update_user_info(user_info, group_id, privileges, connector):
        """
        This function will update the user's information and prep it for synchronization
        :param user_info: dict()
        :param group_id: str
        :param privileges: list[]
        :param connector: dict()
        :return: dict()
        """

        data = None

        if connector == 'umapi':
            data = {
                "email": user_info['username'],
                "firstName": user_info['firstname'],
                "groupId": group_id,
                "lastName": user_info['lastname'],
                "roles": privileges
            }

        elif connector == 'ldap':
            data = {
                "email": user_info['mail'],
                "firstName": user_info['givenName'],
                "lastName": user_info['sn'],
                "company": user_info['company'],
                "groupId": group_id,
                "phone": user_info['mobile'],
                "roles": privileges,
                "title": user_info['title']
            }

        return data

    @staticmethod
    def filter_group(sign_config, group_list, add_ignore_groups):
        """
        This function will filter down the group section in UMAPI user call. It will remove any groups with admin titles
        in it to avoid creating multiple groups.
        :param sign_config: dict()
        :param group_list: list[]
        :param add_ignore_groups: list[]
        :return: list[]
        """

        remove_groups = ['_org_admin', '_PRODUCT_ADMIN', '_deployment_admin', '_support_admin', '_admin_']

        # Append groups that was set in the configuration file
        if add_ignore_groups:
            remove_groups = remove_groups + sign_config['condition']['ignore_groups']
        else:
            remove_groups = remove_groups

        for group in sign_config['condition']['product_group']:
            remove_groups.append(group)

        # Filter out groups with that contain the filter words
        temp_group_list = [group for group in group_list if not any(word in group for word in remove_groups)]

        return temp_group_list
