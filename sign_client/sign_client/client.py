import asyncio
import json
import logging
from math import ceil

import aiohttp
import requests

from .error import AssertionException

from .model import GroupInfo, UsersInfo, DetailedUserInfo, GroupsInfo, UserGroupsInfo, JSONEncoder, DetailedGroupInfo


class SignClient:
    _endpoint = 'api/rest/v6/'
    USER_PAGE_SIZE = 1000
    GROUP_PAGE_SIZE = 1000

    def __init__(self, connection, host, integration_key, admin_email, logger=None):
        self.host = host
        self.integration_key = integration_key
        self.admin_email = admin_email
        self.api_url = None
        self.groups = []
        self.max_sign_retries = connection.get('retry_count') or 5
        self.concurrency_limit = connection.get('request_concurrency') or 1
        timeout = connection.get('timeout') or 120
        self.batch_size = connection.get('batch_size') or 10000
        self.logger = logger or logging.getLogger("sign_client_{}".format(self.integration_key[0:4]))
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout, sock_read=timeout)
        self.loop = asyncio.get_event_loop()
        self.users = {}
        self.user_groups = {}

    def _init(self):
        self.api_url = self.base_uri()
        self.groups = self.get_groups()

    def sign_groups(self):
        if self.api_url is None or self.groups is None:
            self._init()
        return self.groups

    def header(self):
        """
        Return Sign API auth header
        :return: dict()
        """
        return {
            "Authorization": "Bearer {}".format(self.integration_key)
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

        url = 'https://' + self.host + '/' + self._endpoint

        url_path = 'baseUris'
        access_point_key = 'apiAccessPoint'

        result = requests.get(url + url_path, headers=self.header())
        if result.status_code != 200:
            raise AssertionException(
                "Error getting base URI from Sign API, is API key valid? (error: {}, reason: {}, {})".format
                (result.status_code, result.reason, result.content))

        if access_point_key not in result.json():
            raise AssertionException("Error getting base URI for Sign API, result invalid")

        return result.json()[access_point_key] + self._endpoint

    def _paginate_get(self, base_url, list_attr, constructor, page_size) -> list:
        all_results = []
        cursor = None
        while True:
            if cursor is not None:
                cursor_str = f"&cursor={cursor}"
            else:
                cursor_str = ""
            result, _ = self.call_with_retry_sync('GET', f"{base_url}?pageSize={str(page_size)}{cursor_str}", self.header())
            result = constructor(result)
            all_results.extend(getattr(result, list_attr))
            cursor = result.page.nextCursor
            if cursor is None:
                break
        return all_results

    def get_users(self):
        """
        Gets the full user list, and then extracts the user ID's for making calls
        We return self.users because it will be filled by the _get_user method.  This is
        necessary to avoid returning futures of calls which we cannot predict.
        """
        if self.api_url is None or self.groups is None:
            self._init()

        self.logger.info('Getting list of all Sign users')
        user_list = self._paginate_get(f"{self.api_url}users", 'userInfoList', UsersInfo.from_dict, self.USER_PAGE_SIZE)
        user_ids = [u.id for u in user_list]
        self._handle_calls(self._get_user, self.header(), user_ids)
        return self.users


    def get_user_groups(self, user_ids):
        if self.api_url is None or self.groups is None:
            self._init()
        self.logger.info(f'Getting groups for {len(user_ids)} Sign users')
        self._handle_calls(self._get_user_groups, self.header(), user_ids)
        return self.user_groups

    def update_users(self, users):
        """
        Passthrough for call handling
        """
        self._handle_calls(self._update_user, self.header_json(), users)

    def update_user_groups(self, user_groups):
        """
        Passthrough for call handling
        """
        self._handle_calls(self._update_user_groups, self.header_json(), user_groups)

    def get_groups(self):
        """
        API request to get group information
        :return: dict()
        """
        if self.api_url is None:
            self.api_url = self.base_uri()

        self.logger.info('getting Sign user groups')
        groups = self._paginate_get(f"{self.api_url}groups", 'groupInfoList', GroupsInfo.from_dict, self.GROUP_PAGE_SIZE)
        return groups

    def create_group(self, group: DetailedGroupInfo):
        """
        Create a new group in Sign
        :param group: str
        :return:
        """
        if self.api_url is None or self.groups is None:
            self._init()
        url = f"{self.api_url}groups"
        header = self.header_json()
        data = json.dumps(group, cls=JSONEncoder)
        self.logger.info(f'Creating Sign group {group.name}')
        res, code = self.call_with_retry_sync('POST', url, header, data)
        if code > 299:
            raise AssertionException(f"Failed to create Sign group '{group.name}' (reason: {res.reason})")
        self.groups.append(GroupInfo(
            groupName=group.name,
            groupId=group.id,
            createdDate=group.createdDate,
            isDefaultGroup=group.isDefaultGroup,
        ))
        return res['id']

    def insert_user(self, data):
        """
        Insert Sign user
        :param data: dict()
        """
        if self.api_url is None or self.groups is None:
            self._init()

        res = requests.post(self.api_url + 'users', headers=self.header_json(), data=json.dumps(data))
        # Response status code 201 is successful insertion
        if res.status_code != 201:
            raise AssertionException("Failed to insert user '{}' (code: {} reason: {})"
                                     .format(data['email'], res.status_code, res.reason))

    def deactivate_user(self, user_id):
        """
        Deactivate Sign user
        :param data: dict()
        """
        if self.api_url is None or self.groups is None:
            self._init()
        data = {
            "userStatus": 'INACTIVE'
        }
        res = requests.put(self.api_url + 'users/' + user_id + '/status', headers=self.header_json(),
                           data=json.dumps(data))
        # Response status code 200 is successful update
        if res.status_code != 200:
            raise AssertionException("Failed to deactivate user '{}' (code: {} reason: {})"
                                     .format(user_id, res.status_code, res.reason))

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
            if code > 299:
                self.logger.error(f"Error fetching user '{user_id}' with response: {user}")
                return
            user = DetailedUserInfo.from_dict(user)
            if user.email == self.admin_email:
                return
            self.users[user.email] = user
            self.logger.debug(f'retrieved user details for Sign user {user.email}')


    async def _get_user_groups(self, semaphore, user_id, header, session):
        async with semaphore:
            url = f"{self.api_url}users/{user_id}/groups"
            groups, code = await self.call_with_retry_async('GET', url, header, session=session)
            if code > 299:
                self.logger.error(f"Error fetching groups for user '{user_id}' with response: {groups}")
                return
            groups = UserGroupsInfo.from_dict(groups)
            self.user_groups[user_id] = groups
            self.logger.debug(f'retrieved user group details for Sign user {user_id}')

    async def _update_user(self, semaphore, user, headers, session):
        """
        Update Sign user
        """
        # This will block the method from executing until a position opens
        async with semaphore:
            url = f"{self.api_url}users/{user.id}"
            body, code = await self.call_with_retry_async('PUT', url, headers, data=json.dumps(user, cls=JSONEncoder), session=session)
            self.logger.info(f"Updated Sign User: {user.email}")
            if code > 299:
                self.logger.error(f"Error updating user '{user.email}' (code {code}) with response: {body}")

    async def _update_user_groups(self, semaphore, user_group_data, headers, session):
        """
        Update Sign user
        """
        # This will block the method from executing until a position opens
        user_id, group_data = user_group_data
        async with semaphore:
            url = f"{self.api_url}users/{user_id}/groups"
            body, code = await self.call_with_retry_async('PUT', url, headers, data=json.dumps(group_data, cls=JSONEncoder), session=session)
            self.logger.info(f"Updated Sign User: {user_id}")
            if code > 299:
                self.logger.error(f"Error updating user '{user_id}' (code {code}) with response: {body}")

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
                async with session.request(method=method, url=url, data=data or {}) as r:
                    if r.status >= 500:
                        raise AssertionException('{}, Headers: {}'.format(r.status, r.headers))
                    elif r.status == 429:
                        raise AssertionException('{} - too many calls. Headers: {}'.format(r.status, r.headers))
                    body = await r.text()
                    if method != 'PUT':
                        return json.loads(body), r.status
                    else:
                        # PUT calls respond with an empty body
                        return body, r.status
            except Exception as exc:
                retry_nb += 1
                self.logger.warning('Call failed: Type: {} - Message: {}'.format(type(exc), exc))
                if retry_nb == (self.max_sign_retries + 1):
                    raise AssertionException('Quitting after {} retries'.format(self.max_sign_retries))
                self.logger.warning('Waiting for {} seconds before retry'.format(waiting_time))

                await asyncio.sleep(waiting_time)
            finally:
                if close:
                    await session.close()
