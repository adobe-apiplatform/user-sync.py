import requests


class SignClient:
    version = 'v5'
    _endpoint_template = 'api/rest/{}/'

    def __init__(self, config):
        for k in ['host', 'key', 'admin_email']:
            assert k in config, "Key '{}' must be specified for all Sign orgs".format(k)
        self.host = config['host']
        self.key = config['key']
        self.admin_email = config['admin_email']
        self.console_org = config['console_org'] if 'console_org' in config else None
        self.api_url = self.base_uri()

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
            users[user['email']] = user

        return users

    def get_groups(self):
        """
        API request to get group information
        :return: dict()
        """
        groups = {}
        res = requests.get(self.api_url + 'groups', headers=self.header())
        if res.status_code == 200:
            sign_groups = res.json()
            for group in sign_groups['groupInfoList']:
                groups[group['groupName']] = group['groupId']
        return groups
