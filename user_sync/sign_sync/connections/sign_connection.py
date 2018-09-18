import requests
import user_sync.config
import codecs
import json

from user_sync.error import AssertionException

class Sign:

    def __init__(self, logs):

        self.logs = logs
        self.sign_config = self.load_sign_config()

        self.sign_config.yml = self.sign_config.value

        # read server parameters
        self.host = self.sign_config.yml['server']['host']
        self.endpoint = self.sign_config.yml['server']['endpoint_v5']

        # read condition parameters
        self.version = self.sign_config.yml['conditions']['version']
        self.connector = self.sign_config.yml['conditions']['connector']


        # read enterprise parameters
        self.integration = self.sign_config.yml['enterprise']['integration']
        self.email = self.sign_config.yml['enterprise']['email']

        if self.connector == 'umapi':
            self.account_admin = self.sign_config.yml['umapi_conditions']['account_admin_groups']
            self.ignore_admin_group = self.sign_config.yml['umapi_conditions']['ignore_admin_groups']
            self.product_group = self.sign_config.yml['umapi_conditions']['product_group']
            self.ignore_group = self.sign_config.yml['umapi_conditions']['ignore_groups']
        else:
            self.account_admin = None
            self.ignore_admin_group = None

        self.api_counter = 0

    def load_sign_config(self):
        """
        This function loads the Sign YML file into ConfigFileLoader
        :return:
        """

        config_filename = 'sign_sync/connector-sign-sync.yml'
        config_encoding = 'utf-8'
        try:
            codecs.lookup(config_encoding)
        except LookupError:
            raise AssertionException("Unknown encoding '%s' specified for configuration files" % config_encoding)
        user_sync.config.ConfigFileLoader.config_encoding = config_encoding
        main_config_content = user_sync.config.ConfigFileLoader.load_root_config(config_filename)
        return user_sync.config.DictConfig("<%s>" % config_filename, main_config_content)

    def get_sign_url(self, ver=None):
        """
        This function returns the SIGN url.
        :param ver: str
        :return: str
        """

        if ver is None:
            return "https://" + self.host + self.endpoint + "/"
        else:
            return "https://" + self.host + "/" + ver + "/"

    def get_sign_header(self, ver=None):
        """
        This function returns the SIGN header
        :param ver: str
        :return: dict()
        """

        if self.version == 'v5' or ver == 'v5':
            headers = {
                "Access-Token": self.integration
            }
        else:
            headers = {
                "Authorization": "Bearer {}".format(self.integration)
            }

        return headers

    def get_priv_settings(self):
        """
        This function returns a list of admin privileges from SIGN YAML (account_admin_groups)
        :return: list[]
        """

        return self.account_admin

    def get_ignore_priv_settings(self):
        """
        This function return a list of all ignore admin groups from SIGN YAML (ignore_admin_groups)
        :return:
        """

        return self.ignore_admin_group

    def get_ignore_groups_setting(self):
        """
        This function returns a list of all ignore groups from SIGN YAML (ignore_group)
        :return:
        """

        return self.ignore_group

    def get_product_groups_settings(self):
        """
        This function returns a list of product groups from SIGN YAML.
        :return:
        """
        return self.product_group

    def validate_integration_key(self, headers, url):
        """
        This function validates that the SIGN integration key is valid.
        :param headers: dict()
        :param url: str
        :return:
        """

        if self.version == "v5":
            res = requests.get(url + "base_uris", headers=headers)
            self.api_counter += 1
        else:
            res = requests.get(url + "baseUris", headers=headers)
            self.api_counter += 1

        # self.logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        if res.status_code != 200:
            self.logs.error(res.status_code)
            self.logs.error(res.headers)
            self.logs.error(res.text)
            exit(res.status_code)

    def get_config_dict(self):
        """
        This function will grab all the data from the configuration file and create a dict of information
        :return: dict()
        """

        sign_config = dict()
        sign_config['condition'] = dict()
        sign_config['url'] = self.get_sign_url()
        sign_config['header'] = self.get_sign_header()
        sign_config['group'] = self.get_sign_group(sign_config['header'], sign_config['url'])
        sign_config['email'] = self.email
        sign_config['connector'] = self.connector
        sign_config['condition']['ignore_groups'] = self.get_ignore_groups_setting()

        if self.connector == 'umapi':
            sign_config['condition']['account_admin_groups'] = self.get_priv_settings()
            sign_config['condition']['ignore_admin_groups'] = self.get_ignore_priv_settings()
            sign_config['condition']['product_group'] = self.get_product_groups_settings()

        return sign_config

    def reactivate_account(self, sign_config, user_id):
        """
        This function will reactivate a user account that's been inactive
        :param sign_config: dict()
        :param user_id: str
        :return:
        """

        # SIGN API call to get user by ID
        res = requests.get(sign_config['url'] + 'users/' + user_id, headers=sign_config['header'])
        self.api_counter += 1
        data = res.json()

        if data['userStatus'] == "INACTIVE":
            temp_header = self.create_temp_header(sign_config)
            payload = {
                "userStatus": "ACTIVE"
            }

            # SIGN API call to reactivate user account
            res = requests.put(sign_config['url'] + 'users/' + user_id + '/status',
                               headers=temp_header, data=json.dumps(payload))
            self.api_counter += 1

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
            self.api_counter += 1
            # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

            if res.status_code == 201:
                self.logs.info('{} Group Created...'.format(group_name))
                res_data = res.json()
                sign_config['group'][group_name] = res_data['groupId']
            else:
                self.logs.log_error_code(self.logs, res)

    def check_user_existence_in_sign(self, sign_config, email):
        """
        This function checks if the user exist.
        :param sign_config: dict()
        :param email: str
        :return: int & str
        """

        # SIGN API call to get user by email
        res = requests.get(sign_config['url'] + 'users?x-user-email=' + email, headers=sign_config['header'])
        self.api_counter += 1
        data = res.json()

        if res.status_code == 200:
            # self.reactivate_account(sign_config, data['userInfoList'][0]['userId'])
            return data['userInfoList'][0]['userId']
        else:
            return None

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
        self.api_counter += 1
        # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        key = self.get_dict_key(sign_config['group'], group_id)

        if res.status_code == 200:
            self.logs.info('{} information updated to {}...'.format(data['email'], key))

        else:
            self.logs.log_error_code(self.logs, res)


    def get_sign_group(self,header, url):
        """
        This function creates a list of groups that's in Adobe Sign Groups.
        :param header: str
        :param url: str
        :param logs: dict()
        :return: list[]
        """

        res = requests.get(url + 'groups', headers=header)
        self.api_counter += 1

        sign_groups = res.json()

        temp_list = {}

        for group in sign_groups['groupInfoList']:
            temp_list[group['groupName']] = group['groupId']

        return temp_list


    def get_user_data(self, header, url, user_id, logs):

        res = requests.get(url + 'users/' + user_id, headers=header)
        self.api_counter += 1
        data = res.json()

        #API LOG
        logs.info("{} {} {}".format(res.request, res.status_code, res.url))

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

    def print_counter(self):
        print(self.api_counter)