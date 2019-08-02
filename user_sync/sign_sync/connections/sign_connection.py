import requests
import json
import yaml

LOGGER = None


class Sign:

    def __init__(self, logs=None):

        self.logs = logs
        global LOGGER
        LOGGER = self.logs

        try:
            with open("sign_sync/config/connector-sign-sync.yml") as stream:
                try:
                    self.sign_config_yml = yaml.load(stream, Loader=yaml.FullLoader)
                except yaml.YAMLError as exc:
                    print(exc)
        except IOError:
            self.logs['error'].error('** Failed To Open Connector-Sign-Sync.yml **')
            exit(1)

        # Read server parameters
        self.host = self.sign_config_yml['server']['host']
        self.endpoint = self.sign_config_yml['server']['endpoint_v5']

        # Read condition parameters
        self.version = self.sign_config_yml['sign_sync']['version']
        self.connector = self.sign_config_yml['sign_sync']['connector']
        self.account_type = self.sign_config_yml['umapi_conditions']['target_account_type']

        # Read enterprise parameters
        self.integration = self.sign_config_yml['enterprise']['integration']
        self.email = self.sign_config_yml['enterprise']['email']

        if self.connector == 'umapi':
            self.product_profile = self.sign_config_yml['umapi_conditions']['product_profile']
        else:
            self.product_profile = []
            self.account_admin = None

        self.url = self.get_sign_url()
        self.header = self.get_sign_header()
        self.temp_header = self.get_temp_header()

        self.sign_users = self.get_sign_users()
        self.default_group = self.get_sign_group()['Default Group']

    class SignDecorators:
        @classmethod
        def exception_catcher(cls, func):
            def wrapper(*args, **kwargs):
                try:
                    res = func(*args, **kwargs)
                    return res
                except requests.exceptions.HTTPError as http_error:
                    LOGGER['error'].error("-- HTTP ERROR: {} --".format(http_error))
                    exit()
                except requests.exceptions.ConnectionError as conn_error:
                    LOGGER['error'].error("-- ERROR CONNECTING -- {}".format(conn_error))
                    exit()
                except requests.exceptions.Timeout as timeout_error:
                    LOGGER['error'].error("-- TIMEOUT ERROR: {} --".format(timeout_error))
                    exit()
                except requests.exceptions.RequestException as error:
                    LOGGER['error'].error("-- ERROR: {} --".format(error))
                    exit()

            return wrapper

    @SignDecorators.exception_catcher
    def validate_integration_key(self, headers, url):
        """
        This function validates that the SIGN integration key is valid.
        :param headers: dict()
        :param url: str
        :return: dict()
        """

        if self.version == "v5":
            res = requests.get(url + "base_uris", headers=self.header)
        else:
            res = requests.get(url + "baseUris", headers=headers)

        return res

    @SignDecorators.exception_catcher
    def api_get_group_request(self):
        """
        API request to get group information
        :return: dict()
        """

        res = requests.get(self.url + 'groups', headers=self.header)

        return res

    @SignDecorators.exception_catcher
    def api_get_users_request(self):
        """
        API request to get user information from SIGN.
        :return: dict()
        """

        res = requests.get(self.url + 'users', headers=self.header)

        return res

    @SignDecorators.exception_catcher
    def api_post_group_request(self, data):
        """
        API request to post new group in SIGN.
        :param data: list[]
        :return: dict[]
        """

        res = requests.post(self.url + 'groups', headers=self.temp_header, data=json.dumps(data))

        return res

    @SignDecorators.exception_catcher
    def api_put_user_request(self, sign_user_id, data):
        """
        API request to change user group information into SIGN.
        :param sign_user_id: str
        :param data: dict()
        :return: dict()
        """

        res = requests.put(self.url + 'users/' + sign_user_id, headers=self.temp_header, data=json.dumps(data))

        return res

    @SignDecorators.exception_catcher
    def api_get_user_by_id_request(self, user_id):
        """
        API request to get user by ID
        :param user_id:  str
        :return: dict()
        """

        res = requests.get(self.url + 'users/' + user_id, headers=self.header)

        return res

    @SignDecorators.exception_catcher
    def api_put_user_status_request(self, user_id, payload):
        """
        API request to change user status.
        :param user_id: str
        :param payload: dict()
        :return: dict()
        """

        res = requests.put(self.url + 'users/' + user_id + '/status',
                           headers=self.header, data=json.dumps(payload))

        return res

    @SignDecorators.exception_catcher
    def api_post_user_request(self, payload):
        """
        API request to post new user in SIGN.
        :param payload: dict()
        :return: dict()
        """

        res = requests.post(self.url + 'users',
                            headers=self.header, data=json.dumps(payload))

        return res

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

        headers = {}

        if ver == 'v6':
            headers = {
                "Authorization": "Bearer {}".format(self.integration)
            }
        elif self.version == 'v5' or ver == 'v5':
            headers = {
                "Access-Token": self.integration
            }

        return headers

    def get_sign_group(self):
        """
        This function creates a list of groups that's in Adobe Sign Groups.
        :return: list[]
        """

        temp_list = {}

        res = self.api_get_group_request()

        if res.status_code == 200:
            sign_groups = res.json()
            for group in sign_groups['groupInfoList']:
                temp_list[group['groupName']] = group['groupId']

        return temp_list

    def get_product_profile(self):
        """
        This function returns the product profile
        :return: list[]
        """

        return self.product_profile

    def get_sign_users(self):
        """
        This function will create a list of all users in SIGN.
        :return: list[dict()]
        """

        user_list = []
        res = self.api_get_users_request()

        if res.status_code == 200:
            user_list.append(res.json()['userInfoList'])

        return user_list[0]

    def create_sign_group(self, group_list):
        """
        This function will create a group in Adobe SIGN if the group doesn't already exist.
        :param group_list: list[]
        :return:
        """

        sign_group = self.get_sign_group()

        for count, group_name in enumerate(group_list):
            data = {
                "groupName": group_name
            }

            # SIGN API to get existing groups
            res = self.api_post_group_request(data)

            if res.status_code == 201:
                self.logs['process'].info('{} Group Created...'.format(group_name))
                res_data = res.json()
                sign_group[group_name] = res_data['groupId']
            else:
                self.logs['error'].error("!! {}: Creating group error !! {}".format(group_name, res.text))
                self.logs['error'].error('!! Reason !! {}'.format(res.reason))

    def get_temp_header(self):
        """
        This function creates a temp header to push json payloads
        :return: dict()
        """

        temp_header = self.header
        temp_header['Content-Type'] = 'application/json'
        temp_header['Accept'] = 'application/json'

        return temp_header

    def get_user_info(self, user_info, group_id, group=None):
        """
        Retrieve user's information
        :param user_info: dict()
        :param group_id: str
        :param group: list[]
        :return: dict()
        """

        privileges = self.check_umapi_privileges(group, user_info)

        data = {
            "email": user_info['username'],
            "firstName": user_info['firstname'],
            "groupId": group_id,
            "lastName": user_info['lastname'],
            "roles": privileges
        }

        return data

    def get_user_roles(self, user):
        """
        This function will get a list of all active users in Adobe Sign
        :return: list[]
        """
        res = requests.get(self.url + 'users/' + user['userId'], headers=self.header)
        user_data = res.json()

        if 'roles' in user_data:
            user['roles'] = user_data['roles']
        else:
            user['roles'] = 'NORMAL_USER'

        user['sign_group'] = user_data['group']

    @staticmethod
    def check_umapi_privileges(group, umapi_user_info):
        """
        This function will look through the configuration settings and give access privileges access to each user.
        :param group: list[]
        :param umapi_user_info: dict()
        :return:
        """

        roles = umapi_user_info['roles']

        if roles == 'NORMAL_USER':
            privileges = ["NORMAL_USER"]
        elif roles == 'GROUP_ADMIN':
            if group != umapi_user_info['sign_group']:
                privileges = ["NORMAL_USER"]

            else:
                privileges = ['GROUP_ADMIN']
        elif roles == 'ACCOUNT_ADMIN':
            privileges = ["ACCOUNT_ADMIN"]
        else:
            privileges = ["ACCOUNT_ADMIN", "GROUP_ADMIN"]

        return privileges

    def get_updated_user_list(self, user_list):
        """
        This function checks to see if the user exist in SIGN.
        :param user_list: list[dict()]
        :return: list[dict()]
        """

        sign_users = self.get_sign_users()
        updated_user_list = []

        for user in user_list:
            for sign_user in sign_users:
                if user['email'].lower() in sign_user['email'].lower():
                    self.get_user_roles(sign_user)
                    user['userId'] = sign_user['userId']
                    user['roles'] = sign_user['roles']
                    user['sign_group'] = sign_user['sign_group']
                    updated_user_list.append(user)
                    break

        return updated_user_list

    def process_user(self, user):
        """
        This function will process each user and assign them to their Sign groups
        :param user: dict()
        :return:
        """

        temp_group = self.get_sign_group()

        # Sort the groups and assign the user to first group
        # Sign doesn't support multi group assignment at this time
        for group in sorted(user['groups']):
            if group != self.product_profile:
                group_id = temp_group.get(group)
                if group_id is not None:
                    temp_payload = self.get_user_info(user, group_id, group)
                    res = self.api_put_user_request(user['userId'], temp_payload)
                    if res.status_code == 200:
                        self.logs['process'].info('<< Group: {} Roles: {} >> {}'.format(
                            group, user['roles'], user['email']))
                        pass
                    else:
                        self.logs['error'].error("!! Adding User To Group Error !! {} \n{}".format(
                            user['email'], res.text))
                        self.logs['error'].error('!! Reason !! {}'.format(res.reason))
