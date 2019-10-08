import logging
import requests
import json


class SignClient:
    version = 'v5'
    _endpoint_template = 'api/rest/{}/'
    DEFAULT_GROUP_NAME = 'default group'

    def __init__(self, config):
        for k in ['host', 'key', 'admin_email']:
            assert k in config, "Key '{}' must be specified for all Sign orgs".format(k)
        self.host = config['host']
        self.key = config['key']
        self.admin_email = config['admin_email']
        self.console_org = config['console_org'] if 'console_org' in config else None
        self.api_url = self.base_uri()
        self.groups = self.get_groups()
        self.default_group_id, = [_id for name, _id in self.groups.items() if name == self.DEFAULT_GROUP_NAME]
        self.logger = logging.getLogger(self.logger_name())

    def logger_name(self):
        return 'sign_client.{}'.format(self.console_org if self.console_org else 'main')

    def header(self):
        """
        Return Sign API auth header
        :return: dict()
        """
        if self.version == 'v6':
            return {
                "Authorization": "Bearer {}".format(self.key)
            }
        return {
            "Access-Token": self.key
        }

    def header_json(self):
        """
        Get auth headers with options to PUT/POST JSON
        :return: dict()
        """

        json_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        json_headers.update(self.header())
        return json_headers

    def base_uri(self):
        """
        This function validates that the SIGN integration key is valid.
        :return: dict()
        """

        endpoint = self._endpoint_template.format(self.version)
        url = 'https://' + self.host + '/' + endpoint

        if self.version == "v6":
            return requests.get(url + "baseUris", headers=self.header()).json()['apiAccessPoint'] + endpoint
        return requests.get(url + "base_uris", headers=self.header()).json()['api_access_point'] + endpoint

    def get_users(self):
        """
        Get list of all users from Sign (indexed by email address)
        :return: dict()
        """

        users = {}
        self.logger.debug('getting list of all Sign users')
        users_res = requests.get(self.api_url + 'users', headers=self.header())

        assert users_res.status_code == 200, "Error retrieving Sign user list"
        for user_id in map(lambda u: u['userId'], users_res.json()['userInfoList']):
            user_res = requests.get(self.api_url + 'users/' + user_id, headers=self.header())
            assert user_res.status_code == 200, "Error retrieving details for Sign user '{}'".format(user_id)
            user = user_res.json()
            if user['userStatus'] != 'ACTIVE':
                continue
            if user['email'] == self.admin_email:
                continue
            user['userId'] = user_id
            user['roles'] = self.user_roles(user)
            users[user['email']] = user
            self.logger.debug('retrieved user details for Sign user {}'.format(user['email']))

        return users

    def get_groups(self):
        """
        API request to get group information
        :return: dict()
        """
        res = requests.get(self.api_url + 'groups', headers=self.header())
        assert res.status_code == 200, "Error retrieving Sign group list"
        groups = {}
        sign_groups = res.json()
        for group in sign_groups['groupInfoList']:
            groups[group['groupName'].lower()] = group['groupId']
        return groups

    def create_group(self, group):
        """
        Create a new group in Sign
        :param group: str
        :return:
        """
        res = requests.post(self.api_url + 'groups', headers=self.header_json(), data=json.dumps({'groupName': group}))
        assert res.status_code == 201, "Failed to create Sign group '{}' (reason: {})".format(group, res.reason)
        self.groups[group] = res.json()['groupId']

    def update_user(self, user_id, data):
        """
        Update Sign user
        :param user_id: str
        :param data: dict()
        :return: dict()
        """

        res = requests.put(self.api_url + 'users/' + user_id, headers=self.header_json(), data=json.dumps(data))
        assert res.status_code == 200, "Failed to update user '{}' (reason: {})".format(user_id, res.reason)

    @staticmethod
    def user_roles(user):
        """
        Resolve user roles
        :return: list[]
        """
        return ['NORMAL_USER'] if 'roles' not in user else user['roles']
