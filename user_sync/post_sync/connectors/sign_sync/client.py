import logging
import requests
import json
from user_sync.error import AssertionException


class SignClient:
    version = 'v5'
    _endpoint_template = 'api/rest/{}/'
    DEFAULT_GROUP_NAME = 'default group'

    def __init__(self, config):
        for k in ['host', 'key', 'admin_email']:
            if k not in config:
                raise AssertionException("Key '{}' must be specified for all Sign orgs".format(k))
        self.host = config['host']
        self.key = config['key']
        self.admin_email = config['admin_email']
        self.console_org = config['console_org'] if 'console_org' in config else None
        self.api_url = None
        self.groups = None
        self.logger = logging.getLogger(self.logger_name())

    def _init(self):
        self.api_url = self.base_uri()
        self.groups = self.get_groups()

    def sign_groups(self):
        if self.api_url is None or self.groups is None:
            self._init()
        return self.groups

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
            url_path = 'baseUris'
            access_point_key = 'apiAccessPoint'
        else:
            url_path = 'base_uris'
            access_point_key = 'api_access_point'

        result = requests.get(url + url_path, headers=self.header())
        if result.status_code != 200:
            raise AssertionException("Error getting base URI from Sign API, is API key valid?")

        if access_point_key not in result.json():
            raise AssertionException("Error getting base URI for Sign API, result invalid")

        return result.json()[access_point_key] + endpoint

    def get_users(self):
        """
        Get list of all users from Sign (indexed by email address)
        :return: dict()
        """
        if self.api_url is None or self.groups is None:
            self._init()
        users = {}
        self.logger.debug('getting list of all Sign users')
        users_res = requests.get(self.api_url + 'users', headers=self.header())
        if users_res.status_code != 200:
            raise AssertionException("Error retrieving Sign user list")
        for user_id in map(lambda u: u['userId'], users_res.json()['userInfoList']):
            user_res = requests.get(self.api_url + 'users/' + user_id, headers=self.header())
            if users_res.status_code != 200:
                raise AssertionException("Error retrieving details for Sign user '{}'".format(user_id))
            user = user_res.json()
            user_status = user.get('userStatus')
            if user_status and user_status != 'ACTIVE':
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
        if self.api_url is None:
            self.api_url = self.base_uri()

        res = requests.get(self.api_url + 'groups', headers=self.header())
        if res.status_code != 200:
            raise AssertionException("Error retrieving Sign group list")
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
        if self.api_url is None or self.groups is None:
            self._init()
        res = requests.post(self.api_url + 'groups', headers=self.header_json(), data=json.dumps({'groupName': group}))
        if res.status_code != 201:
            raise AssertionException("Failed to create Sign group '{}' (reason: {})".format(group, res.reason))
        self.groups[group] = res.json()['groupId']

    def update_user(self, user_id, data):
        """
        Update Sign user
        :param user_id: str
        :param data: dict()
        :return: dict()
        """
        if self.api_url is None or self.groups is None:
            self._init()

        res = requests.put(self.api_url + 'users/' + user_id, headers=self.header_json(), data=json.dumps(data))
        if res.status_code != 200:
            raise AssertionException("Failed to update user '{}' (reason: {})".format(user_id, res.reason))

    @staticmethod
    def user_roles(user):
        """
        Resolve user roles
        :return: list[]
        """
        return ['NORMAL_USER'] if 'roles' not in user else user['roles']
