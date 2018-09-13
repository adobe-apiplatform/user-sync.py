import requests
import json
import pprint

from sign_sync.connections.umapi_connection import UMAPIConfig
from sign_sync.connections.sign_connection import SIGNConfig
from sign_sync.connections.ldap_connection import LDAPConfig
from sign_sync.logger import Log


def run():

    # Create process, api, and error loggers for Sign Sync
    sign_sync_logs = Log()
    logs = sign_sync_logs.get_logs()

    logs['process'].info('---------------------------------- Starting Sign Sync ----------------------------------')

    # Load SIGN configuration
    sign_obj = SIGNConfig(logs)
    sign_config = sign_obj.get_config_dict()

    # Load LDAP configuration
    ldap_config = LDAPConfig(logs)

    # Load UMAPI configuration
    umapi_obj = UMAPIConfig(logs)
    umapi_config = umapi_obj.get_umapi_config_dict()

    # Sync Admin Console w/ Adobe Sign Console
    user_list = get_umapi_user_list(umapi_obj, umapi_config['header'], logs)
    user_list = get_user_sign_id(user_list, sign_config, logs)
    group_list = parse_groups(sign_config, user_list)
    create_sign_group(group_list, sign_config, logs)
    process_user(user_list, sign_config, ldap_config, logs)

    logs['process'].info('---------------------------------- Ending Sign Sync -----------------------------------')


def process_user(user_list, sign_config, ldap_config, logs):
    """
    This function will process each user and assign them to their Sign groups
    :param user_list:
    :param sign_config:
    :param ldap_config:
    :param logs:
    :return:
    """

    multi_group = sign_config['condition']['multi_group']

    # Iterate through each user from the user list
    for user in user_list:
        if user['email'] == 'nathannguyen345@gmail.com':
            pass
        else:
            name = "{} {}".format(user['firstname'], user['lastname'])
            filter_group_list = filter_group(sign_config, user['groups'], False)

            # If the user is not in a group we will assign them to a default group
            if len(filter_group_list) == 0:
                default_group_id = sign_config['group'].get('Default Group')
                temp_data = get_user_info(user, sign_config, default_group_id)
                temp_data.update(ldap_config.get_extra_ldap_attribute(name))
                add_user_to_sign_group(sign_config, user['id'], default_group_id, temp_data, logs)

            # Sort the groups and assign the user to first group
            # Sign doesn't support multi group assignment at this time
            else:
                for group in sorted(user['groups']):
                    group_id = sign_config['group'].get(group)

                    if group_id is not None and group not in sign_config['condition']['ignore_groups']:
                        temp_data = get_user_info(user, sign_config, group_id, group)
                        temp_data.update(ldap_config.get_extra_ldap_attribute(name))
                        add_user_to_sign_group(sign_config, user['id'], group_id, temp_data, logs)

                        if not multi_group:
                            break


def get_dict_key(group, value):
    """
    Get keys for dict
    :param group: dict()
    :param value: str
    :return: str
    """
    return [key for key, v in group.items() if v == value]


def get_umapi_user_list(umapi_obj, umapi_header, logs):
    """
    This function will create a list of users that's in Adobe Admin Console.
    :param umapi_obj: object
    :param umapi_header: str
    :param logs: dict()
    :return: list[]
    """

    umapi_user_url = umapi_obj.get_custom_url("users")
    page_number = 0
    user_list = list()

    # Request a UMAPI call to grab a list of users until it reaches the last page
    while True:
        res = requests.get(umapi_user_url + "/{}".format(page_number), headers=umapi_header)
        try:
            res.raise_for_status()
            data = res.json()
            user_list.append(data['users'])
            # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

            if data['lastPage']:
                break
            else:
                page_number += 1
        except requests.HTTPError:
            logs.log_error_code(logs, res)

    return user_list[0]


def get_user_sign_id(user_list, sign_config, logs):
    """
    This function will grab all User ID in Adobe Sign for list of users
    :param user_list: list[]
    :param sign_config: dict()
    :param logs: dict()
    :return: list[]
    """

    temp_user_list = list()

    # Iterate through the user list and convert emails with + to %2B
    for user in user_list:
        user_email = user['email']

        if '+' in user_email:
            user_email = user_email.replace('+', '%2B')

        if 'groups' in user and any(x in sign_config['condition']['product_group'] for x in user['groups']):
            sign_user_id = check_user_existence_in_sign(sign_config, user_email, logs)

            if sign_user_id is not None:
                user['id'] = sign_user_id
                temp_user_list.append(user)

    return temp_user_list


def parse_groups(sign_config, user_list):
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
    temp_group_list = filter_group(sign_config, temp_group_list, True)
    temp_group_list = [group for group in temp_group_list if group not in sign_config['group']]

    return temp_group_list


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


def check_user_existence_in_sign(sign_config, email, logs):
    """
    This function checks if the user exist.
    :param sign_config: dict()
    :param email: str
    :param logs: dict()
    :return: int & str
    """

    # SIGN API call to get user by email
    res = requests.get(sign_config['url'] + 'users?x-user-email=' + email, headers=sign_config['header'])
    data = res.json()

    # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

    if res.status_code == 200:
        reactivate_account(sign_config, data['userInfoList'][0]['userId'])
        return data['userInfoList'][0]['userId']
    else:
        return None


def reactivate_account(sign_config, user_id):
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
        temp_header = create_temp_header(sign_config)
        payload = {
            "userStatus": "ACTIVE"
        }

        # SIGN API call to reactivate user account
        res = requests.put(sign_config['url'] + 'users/' + user_id + '/status',
                           headers=temp_header, data=json.dumps(payload))


def create_sign_group(group_list, sign_config, logs):
    """
    This function will create a group in Adobe SIGN if the group doesn't already exist.
    :param group_list: list[]
    :param sign_config: dict()
    :param logs: dict()
    :return:
    """

    temp_header = create_temp_header(sign_config)

    for group_name in group_list:
        data = {
            "groupName": group_name
        }
        # SIGN API to get existing groups
        res = requests.post(sign_config['url'] + 'groups', headers=temp_header, data=json.dumps(data))
        # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        if res.status_code == 201:
            logs['process'].info('{} Group Created...'.format(group_name))
            res_data = res.json()
            sign_config['group'][group_name] = res_data['groupId']
        else:
            logs.log_error_code(logs, res)


def add_user_to_sign_group(sign_config, sign_user_id, group_id, data, logs):
    """
    This function will add users into the SIGN groups.
    :param sign_config: dict()
    :param sign_user_id: str
    :param group_id: str
    :param data: dict()
    :param logs: dict()
    :return:
    """

    temp_header = create_temp_header(sign_config)

    # SIGN API call to put user in the correct group
    res = requests.put(sign_config['url'] + 'users/' + sign_user_id, headers=temp_header, data=json.dumps(data))
    # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

    key = get_dict_key(sign_config['group'], group_id)

    if res.status_code == 200:
        logs['process'].info('{} information updated to {}...'.format(data['email'], key))

    else:
        logs.log_error_code(logs, res)


def get_user_info(user_info, sign_config, group_id, group=None):
    """
    Retrieve user's information
    :param user_info: dict()
    :param sign_config: dict()
    :param group_id: str
    :param group: list[]
    :return: dict()
    """

    privileges = check_umapi_privileges(group, user_info, sign_config['condition'])
    data = update_user_info(user_info, group_id, privileges, sign_config['connector'])

    return data


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
