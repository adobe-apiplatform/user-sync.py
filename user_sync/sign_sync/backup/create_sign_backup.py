import requests
import json
import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from connections.sign_connection import SIGNConfig
from logger import Log

from pathlib import Path

def run(logs):

    p = Path(__file__).parents[1]

    # Load SIGN configuration
    sign_obj = SIGNConfig(logs, p)
    sign_config = sign_obj.get_config_dict()
    sign_obj.validate_integration_key(sign_config['header'], sign_config['url'])

    # Create user data JSON file
    active_user_list, user_id_list = get_active_users(sign_config)
    user_info_list = parse_user_list(active_user_list)
    write_to_file(user_info_list, user_id_list)


def get_active_users(sign_config):
    """
    This function will gather a list of user data from SIGN if the user is an active user.
    :param sign_config: dict()
    :return: list[], list[]
    """

    # SIGN API call to get all users
    res = requests.get(sign_config['url'] + 'users', headers=sign_config['header'])
    data = res.json()
    active_users = list()
    user_id_list = list()

    # Make SIGN API request to see if a user is active and store user information
    for user in data['userInfoList']:
        # SIGN API call to get user by ID
        res = requests.get(sign_config['url'] + 'users/' + user['userId'], headers=sign_config['header'])
        user_data = res.json()

        if user_data['userStatus'] == 'ACTIVE':
            active_users.append(user_data)
            user_id_list.append(user['userId'])

    return active_users, user_id_list

def parse_user_list(active_user_list):
    """
    This function will parse out user info to meet minimum schema criteria for SIGN API update user call.
    :param active_user_list: list[]
    :return: list[]
    """

    user_info = list()
    for user in active_user_list:
        # Skip main account ID since we don't want to change anything relating to the main account
        if user['email'] == 'nathannguyen345@gmail.com':
            pass
        else:
            email = user['email']
            first_name = user['firstName']
            group_id = user['groupId']
            last_name = user['lastName']

            # Condition to see if roles exist in user dict
            if 'roles' not in user:
                roles = ['NORMAL_USER']
            else:
                if len(user['roles']) == 2:
                    roles = user['roles']
                else:
                    roles = user['roles'].split()

            # Create a data dict to store parsed user information
            data = {
                "email": email,
                "firstName": first_name,
                "groupId": group_id,
                "lastName": last_name,
                "roles": roles
            }

            user_info.append(data)

    return user_info

def write_to_file(user_info_list, user_id_list):
    """
    This function will write the user information into a json file.
    :param user_info_list: list[]
    :param user_id_list: list[]
    :return:
    """

    with open('sign_backup_file.json', 'w') as file:
        json.dump(user_info_list, file, ensure_ascii=False)

    with open('user_id_file.txt', 'w') as id_file:
        for id in user_id_list:
            id_file.write("{}\n".format(id))


if __name__ == '__main__':
    p = Path(__file__).parents[2]
    log = Log(p)
    my_log = log.get_log()
    run(my_log)