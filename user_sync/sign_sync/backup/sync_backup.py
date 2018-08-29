import requests
import json
import sys
import os.path
import pprint

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

    sign_backup_file = Path('sign_backup_file.json')
    user_id_file = Path('user_id_file.txt')
    if sign_backup_file.is_file() and user_id_file.is_file():
        user_data_list, user_id_list = load_sign_backup()
        sync_user_data_to_sign(sign_config, user_data_list, user_id_list)
    else:
        print('no file')

def load_sign_backup():
    """
    This function will load the sign backup json and append user information to a list.
    :return: list[]
    """

    with open('sign_backup_file.json', 'r') as file:
        data = json.load(file)

    user_data_list = list()
    for user_data in data:
        user_data_list.append(user_data)

    with open('user_id_file.txt', 'r') as id_file:
        user_id_list = id_file.read().split()

    return user_data_list, user_id_list

def sync_user_data_to_sign(sign_config, user_data_list, user_id_list):

    temp_header = create_temp_header(sign_config)
    for index, data in enumerate(user_data_list):
        res = requests.put(sign_config['url'] + "users/" + user_id_list[index],
                           headers=temp_header, data=json.dumps(data))

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

if __name__ == '__main__':
    p = Path(__file__).parents[2]
    log = Log(p)
    my_log = log.get_log()
    run(my_log)