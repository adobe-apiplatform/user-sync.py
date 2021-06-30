import asyncio
import json
import logging
from math import ceil

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
        connection_cfg = config.get('connection') or {}
        self.max_sign_retries = connection_cfg.get('retry_count') or 5
        self.concurrency_limit = connection_cfg.get('request_concurrency') or 1
        timeout = connection_cfg.get('timeout') or 120
        self.batch_size = connection_cfg.get('batch_size') or 10000
        self.ssl_cert_verify = connection_cfg.get('ssl_cert_verify') or True
        self.logger = logging.getLogger(self.logger_name())
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout, sock_read=timeout)
        self.loop = asyncio.get_event_loop()
        self.users = {}

    def _init(self):
        self.api_url = self.base_uri()
        self.groups = self.get_groups()
        self.reverse_groups = {v: k for k, v in self.groups.items()}

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

        if self.version == 'v6':
            url_path = 'baseUris'
            access_point_key = 'apiAccessPoint'
        else:
            url_path = 'base_uris'
            access_point_key = 'api_access_point'

        result = requests.get(url + url_path, headers=self.header(), verify=self.ssl_cert_verify)
        if result.status_code != 200:
            raise AssertionException('Error getting base URI from Sign API, is API key valid?')

        if access_point_key not in result.json():
            raise AssertionException('Error getting base URI for Sign API, result invalid')
        self.logger.debug('base_uri result: {}'.format(result.json()[access_point_key] + endpoint))

        return result.json()[access_point_key] + endpoint

    def get_groups(self):
        """
        API request to get group information
        :return: dict()
        """
        if self.api_url is None:
            self.api_url = self.base_uri()
        url = self.api_url + 'groups'
        header = self.header()
        sign_groups, code = self.call_with_retry_sync('GET', url, header)
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
        res, code = self.call_with_retry_sync('POST', url, header, data)
        self.groups[group] = res['groupId']

    def update_users(self, users):
        """
        Passthrough for call handling
        """
        self._handle_calls(self._update_user, self.header_json(), users)

    def get_users(self):
        """
        Gets the full user list, and then extracts the user ID's for making calls
        We return self.users because it will be filled by the _get_user method.  This is
        necessary to avoid returning futures of calls which we cannot predict.
        """
        self.logger.info('Getting list of all Sign users')
        user_list, _ = self.call_with_retry_sync('GET', self.api_url + 'users', self.header())

        user_ids = [u['userId'] for u in user_list['userInfoList']]
        self._handle_calls(self._get_user, self.header(), user_ids)
        return self.users

    def _handle_calls(self, handle, headers, objects):
        """
        Batches and executes handle for each of o in objects
        handle: reference to function which will be called
        headers: api headers (common to all requests)
        objects: list of objects, which will be iterated through - and handle called on each
        """

        if self.api_url is None or self.groups is None:
            self._init()

        # Execute calls by batches.  This reduces the memory stack, since we do not need to create all
        # coroutines before starting execution.  We call run_until_complete for each set until all sets have run
        set_number = 1
        batch_count = ceil(len(objects) / self.batch_size)
        for i in range(0, len(objects), self.batch_size):
            self.logger.info("{}s - batch {}/{}".format(handle.__name__, set_number, batch_count))
            self.loop.run_until_complete(self._await_calls(handle, headers, objects[i:i + self.batch_size]))
            set_number += 1

    async def _await_calls(self, handle, headers, objects):
        """
        Where we actually await the coroutines. Must be own method, in order to be handled by loop
        """

        if not objects:
            return 

        # Semaphore specifies number of allowed calls at one time
        sem = asyncio.Semaphore(value=self.concurrency_limit)

        # We must use only 1 session, else will hang
        async with aiohttp.ClientSession(trust_env=True, timeout=self.timeout) as session:
            # prepare a list of calls to make * Note: calls are prepared by using call
            # syntax (eg, func() and not func), but they will not be run until executed by the wait
            # split into batches of self.bach_size to avoid taking too much memory
            calls = [handle(sem, o, headers, session) for o in objects]
            await asyncio.wait(calls)

    async def _get_user(self, semaphore, user_id, header, session):

        # This will block the method from executing until a position opens
        async with semaphore:
            user_url = self.api_url + 'users/' + user_id
            user, code = await self.call_with_retry_async('GET', user_url, header, session=session)
            if code != 200:
                self.logger.error("Error fetching user '{}' with response: {}".format(user_id, user))
                return
            if user['userStatus'] != 'ACTIVE':
                return
            if user['email'] == self.admin_email:
                return
            user['userId'] = user_id
            user['roles'] = self.user_roles(user)
            self.users[user['email']] = user
            self.logger.debug('retrieved user details for Sign user {}'.format(user['email']))

    async def _update_user(self, semaphore, user, headers, session):
        """
        Update Sign user
        """
        # This will block the method from executing until a position opens
        async with semaphore:
            url = self.api_url + 'users/' + user['userId']
            group = self.reverse_groups[user['groupId']]
            body, code = await self.call_with_retry_async('PUT', url, headers, data=json.dumps(user), session=session)
            self.logger.info(
                "Updated Sign user '{}', Group: '{}', Roles: {}".format(user['email'], group, user['roles']))
            if code != 200:
                self.logger.error("Error updating user '{}' with response: {}".format(user['email'], body))

    @staticmethod
    def user_roles(user):
        """
        Resolve user roles
        :return: list[]
        """
        return ['NORMAL_USER'] if 'roles' not in user else user['roles']

    def call_with_retry_sync(self, method, url, header, data=None):
        """
        Need to define this method, so that it can be called outside async context
        loop will execute a single synchronous call, but sharing code with the async retry method
        """
        return self.loop.run_until_complete(self.call_with_retry_async(method, url, header, data=data or {}))

    async def call_with_retry_async(self, method, url, header, data=None, session=None):
        """
        Call manager with exponential retry
        :return: Response <Response> object
        """
        retry_nb = 0
        waiting_time = 10
        close = session is None
        session = session or aiohttp.ClientSession(trust_env=True, timeout=self.timeout)
        session.headers.update(header)
        while True:
            try:
                waiting_time *= 3
                self.logger.debug('Attempt {} to call: {}'.format(retry_nb, url))
                async with session.request(method=method, url=url, data=data or {}, ssl=self.ssl_cert_verify) as r:
                    if r.status >= 500:
                        raise Exception('{}, Headers: {}'.format(r.status, r.headers))
                    elif r.status == 429:
                        raise Exception('{} - too many calls. Headers: {}'.format(r.status, r.headers))
                    elif r.status > 400 and r.status < 500:
                        self.logger.critical(' {} - {}. Headers: {}'.format(r.status, r.reason, r.headers))
                        raise AssertionException('')
                    body = await r.json()
                    return body, r.status
            except Exception as exp:
                retry_nb += 1
                self.logger.warning('Failed: {} - {}'.format(type(exp), exp.args))
                if retry_nb == (self.max_sign_retries + 1):
                    raise AssertionException('Quitting after {} retries'.format(self.max_sign_retries))
                self.logger.warning('Waiting for {} seconds'.format(waiting_time))
                await asyncio.sleep(waiting_time)
            finally:
                if close:
                    await session.close()
