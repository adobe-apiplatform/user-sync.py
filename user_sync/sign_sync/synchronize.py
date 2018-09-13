import requests
import json
import six
import pprint

import user_sync.rules

from sign_sync.connections.umapi_connection import UMAPIConfig
from sign_sync.connections.sign_connection import SIGNConfig
from sign_sync.connections.ldap_connection import LDAPConfig

class Synchronize:

    def __init__(self, logger, config_loader, connector):

        # Create process, api, and error loggers for Sign Sync
        self.logs = logger
        self.config_loader = config_loader
        self.connector = connector

        # Instantiate Sign object
        self.sign_obj = SIGNConfig(self.logs)

        # Instantiate LDAP object
        self.ldap_obj = LDAPConfig(self.config_loader, self.connector.directory, self.logs)

        # Instantiate UMAPI object
        self.umapi_obj = UMAPIConfig(self.config_loader, self.connector.umapi, self.logs)

        self.run()

    def run(self):

        self.logs.info('------------------------------- Starting Sign Sync -------------------------------')

        # Get Sign config & validate integration key
        sign_config = self.sign_obj.get_config_dict()
        self.sign_obj.validate_integration_key(sign_config['header'], sign_config['url'])

        # Authenticate LDAP
        self.ldap_obj.authenticate()

        # Get UMAPI configuration dict
        umapi_config = self.umapi_obj.get_umapi_config_dict()

        # Sync Admin Console w/ Adobe Sign Console
        umapi_connectors = self.get_umapi_connectors()
        umapi_primary_connector = umapi_connectors.get_primary_connector()
        umapi_user_list =  umapi_primary_connector.get_users()
        user_list = self.get_user_sign_id(umapi_user_list, sign_config)
        # group_list = self.parse_groups(sign_config, user_list)
        # self.create_sign_group(group_list, sign_config)
        # self.process_user(user_list, sign_config, self.ldap_obj)

        self.logs.info('------------------------------- Ending Sign Sync ---------------------------------')


    def process_user(self, user_list, sign_config, ldap_config):
        """
        This function will process each user and assign them to their Sign groups
        :param user_list:
        :param sign_config:
        :param ldap_config:
        :return:
        """

        # Iterate through each user from the user list
        for user in user_list:
            if user['email'] == sign_config['email']:
                pass
            else:
                name = "{} {}".format(user['firstname'], user['lastname'])
                filter_group_list = self.filter_group(sign_config, user['groups'], False)

                # If the user is not in a group we will assign them to a default group
                if len(filter_group_list) == 0:
                    default_group_id = sign_config['group'].get('Default Group')
                    temp_data = self.get_user_info(user, sign_config, default_group_id)
                    temp_data.update(ldap_config.get_extra_ldap_attribute(name))
                    self.add_user_to_sign_group(sign_config, user['id'], default_group_id, temp_data)

                # Sort the groups and assign the user to first group
                # Sign doesn't support multi group assignment at this time
                else:
                    for group in sorted(user['groups']):
                        group_id = sign_config['group'].get(group)

                        if group_id is not None and group not in sign_config['condition']['ignore_groups']:
                            temp_data = self.get_user_info(user, sign_config, group_id, group)
                            temp_data.update(ldap_config.get_extra_ldap_attribute(name))
                            self.add_user_to_sign_group(sign_config, user['id'], group_id, temp_data)
                            break


    def get_umapi_connectors(self):
        """
        This function will create a list of users that's in Adobe Admin Console.
        :param umapi_obj: object
        :param umapi_header: str
        :return: list[]
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

            if '+' in user_email:
                user_email = user_email.replace('+', '%2B')

            if 'groups' in user and any(x in sign_config['condition']['product_group'] for x in user['groups']):
                sign_user_id = self.check_user_existence_in_sign(sign_config, user_email)

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


    def check_user_existence_in_sign(self, sign_config, email):
        """
        This function checks if the user exist.
        :param sign_config: dict()
        :param email: str
        :return: int & str
        """

        # SIGN API call to get user by email
        res = requests.get(sign_config['url'] + 'users?x-user-email=' + email, headers=sign_config['header'])
        data = res.json()

        # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        if res.status_code == 200:
            self.reactivate_account(sign_config, data['userInfoList'][0]['userId'])
            return data['userInfoList'][0]['userId']
        else:
            return None


    def reactivate_account(self, sign_config, user_id):
        """
        This function will reactivate a user account that's been inactive
        :param sign_config: dict()
        :param user_id: str
        :return:
        """

        # SIGN API call to get user by ID
        res = requests.get(sign_config['url'] + 'users/' + user_id, headers=sign_config['header'])
        data = res.json()

        if data['userStatus'] == "INACTIVE":
            temp_header = self.create_temp_header(sign_config)
            payload = {
                "userStatus": "ACTIVE"
            }

            # SIGN API call to reactivate user account
            res = requests.put(sign_config['url'] + 'users/' + user_id + '/status',
                               headers=temp_header, data=json.dumps(payload))


    def create_sign_group(self, group_list, sign_config):
        """
        This function will create a group in Adobe SIGN if the group doesn't already exist.
        :param group_list: list[]
        :param sign_config: dict()
        :return:
        """

        temp_header = self.create_temp_header(sign_config)

        for group_name in group_list:
            data = {
                "groupName": group_name
            }
            # SIGN API to get existing groups
            res = requests.post(sign_config['url'] + 'groups', headers=temp_header, data=json.dumps(data))
            # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

            if res.status_code == 201:
                self.logs.info('{} Group Created...'.format(group_name))
                res_data = res.json()
                sign_config['group'][group_name] = res_data['groupId']
            else:
                self.logs.log_error_code(self.logs, res)


    def add_user_to_sign_group(self, sign_config, sign_user_id, group_id, data):
        """
        This function will add users into the SIGN groups.
        :param sign_config: dict()
        :param sign_user_id: str
        :param group_id: str
        :param data: dict()
        :return:
        """

        temp_header = self.create_temp_header(sign_config)

        # SIGN API call to put user in the correct group
        res = requests.put(sign_config['url'] + 'users/' + sign_user_id, headers=temp_header, data=json.dumps(data))
        # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        key = self.get_dict_key(sign_config['group'], group_id)

        if res.status_code == 200:
            self.logs.info('{} information updated to {}...'.format(data['email'], key))

        else:
            self.logs.log_error_code(self.logs, res)


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
    def create_temp_header(sign_config):
        """
        This function creates a temp header to push json payloads
        :param sign_config: dict()
        :return: dict()
        """

        temp_header = sign_config['header']
        temp_header['Content-Type'] = 'application/json'
        temp_header['Accept'] = 'application/json'

        return temp_header

    @staticmethod
    def get_dict_key(group, value):
        """
        Get keys for dict
        :param group: dict()
        :param value: str
        :return: str
        """

        return [key for key, v in group.items() if v == value]