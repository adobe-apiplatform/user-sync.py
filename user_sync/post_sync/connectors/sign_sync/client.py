import asyncio
import json
import logging
import time

import aiohttp
import requests

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
        self.max_sign_retries = 3
        self.sign_timeout = 120
        self.concurrency_limit = 5
        self.logger = logging.getLogger(self.logger_name())
        logging.getLogger("urllib3").setLevel(logging.WARNING)

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
                'Authorization': "Bearer {}".format(self.key),
                'Connection': 'close',
            }
        return {
            'Access-Token': self.key,
            # 'Connection': 'close',
        }

    def header_json(self):
        """
        Get auth headers with options to PUT/POST JSON
        :return: dict()
        """

        json_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Connection': 'close',
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

        if self.version == 'v6':
            url_path = 'baseUris'
            access_point_key = 'apiAccessPoint'
        else:
            url_path = 'base_uris'
            access_point_key = 'api_access_point'

        result = requests.get(url + url_path, headers=self.header())
        if result.status_code != 200:
            raise AssertionException('Error getting base URI from Sign API, is API key valid?')

        if access_point_key not in result.json():
            raise AssertionException('Error getting base URI for Sign API, result invalid')
        self.logger.debug('base_uri result: {}'.format(result.json()[access_point_key] + endpoint))

        return result.json()[access_point_key] + endpoint

    async def call_with_async(self, method, url, header, data=None):
        """
        Call manager with exponential retry
        :return: Response <Response> object
        """
        retry_nb = 1
        waiting_time = 20
        while True:
            try:
                waiting_time *= 3
                self.logger.debug('Attempt {} to call: {}'.format(retry_nb, url))
                async with aiohttp.ClientSession(headers=header) as session:
                    async with session.request(method=method, url=url, data=data or {}) as r:
                        if r.status >= 500:
                            raise Exception('{}, Headers: {}'.format(r.status, r.headers))
                        elif r.status == 429:
                            raise Exception('{} - too many calls. Headers: {}'.format(r.status, r.headers))
                        elif r.status > 400 and r.status < 500:
                            self.logger.critical(' {} - {}. Headers: {}'.format(r.status, r.reason, r.headers))
                            raise AssertionException('')
                        body = await r.json()
                        return body
            except Exception as exp:
                self.logger.warning('Failed: {}'.format(exp))
                if retry_nb == (self.max_sign_retries + 1):
                    raise AssertionException('Quitting after {} retries'.format(self.max_sign_retries))
                self.logger.warning('Waiting for {} seconds'.format(waiting_time))
                time.sleep(waiting_time)
                retry_nb += 1

    def call_with_retry_sync(self, method, url, header, data=None):

        # loop will execute a single synchronous call, but sharing code with the async retry method
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(self.call_with_async(method, url, header, data=data or {}))
        return res

    def get_users(self):
        """
        Get list of all users from Sign (indexed by email address)
        :return: dict()
        """

        if self.api_url is None or self.groups is None:
            self._init()

        header = self.header()
        users_url = self.api_url + 'users'
        self.logger.info('getting list of all Sign users')

        # Synchronous call to get user list, which will be distributed to asyncio
        users_res = self.call_with_retry_sync('GET', users_url, header)

        # Also define self.users = {} to use as receptacle for users.  Important to
        # use self context because we cannot easily return values from our get calls
        # Instead, they concurrently add to the users dict, and we will return it
        # at the end when it is finished
        calls = []
        self.users = {}

        # Semaphore specifies number of allowed calls at one time
        sem = asyncio.Semaphore(value=self.concurrency_limit)

        # prepare a list of calls to make * Note: calls are prepared by using call
        # syntax (eg, func() and not func), but they will not be run until executed
        # by the loop
        for user_id in map(lambda u: u['userId'], users_res['userInfoList']):
            calls.append(self.get_sign_user(sem, user_id, header))

        # loop will execute the tasks
        # wait for all calls to finish
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(calls))

        # return so as to comply with existing code calling this function
        # *prefer instance var to awaiting coroutine results as we cannot
        # guarantee they will be user obj
        return self.users

    # Note the async def - this function can only be executed in asyncio context
    async def get_sign_user(self, semaphore, user_id, header):

        # This will block the method from executing until a position opens
        await semaphore.acquire()

        user_url = self.api_url + 'users/' + user_id
        user = await self.call_with_async('GET', user_url, header)
        if user['userStatus'] != 'ACTIVE':
            return
        if user['email'] == self.admin_email:
            return
        user['userId'] = user_id
        user['roles'] = self.user_roles(user)
        self.users[user['email']] = user
        self.logger.debug('retrieved user details for Sign user {}'.format(user['email']))

        # Release the worker back to pool
        semaphore.release()

    def get_groups(self):
        """
        API request to get group information
        :return: dict()
        """
        if self.api_url is None:
            self.api_url = self.base_uri()
        url = self.api_url + 'groups'
        header = self.header()
        sign_groups = self.call_with_retry_sync('GET', url, header)
        self.logger.info('getting Sign user groups')
        groups = {}
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
        url = self.api_url + 'groups'
        header = self.header_json()
        data = json.dumps({'groupName': group})
        self.logger.info('Creating Sign group {} '.format(group))
        res = self.call_with_retry_sync('POST', url, header, data)
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
        url = self.api_url + 'users/' + user_id
        header = self.header_json()
        json_data = json.dumps(data)
        self.call_with_retry_sync('PUT', url, header, json_data)

    @staticmethod
    def user_roles(user):
        """
        Resolve user roles
        :return: list[]
        """
        return ['NORMAL_USER'] if 'roles' not in user else user['roles']