import logging
from collections import defaultdict

from user_sync.config import DictConfig
from user_sync.error import AssertionException
from user_sync.post_sync import PostSyncConnector
from user_sync.rules import AdobeGroup
from .client import SignClient


class SignConnector(PostSyncConnector):
    name = 'sign_sync'

    def __init__(self, config_options, test_mode=False):
        super().__init__()
        self.logger = logging.getLogger(self.name)
        sync_config = DictConfig('<%s configuration>' % self.name, config_options)
        self.user_groups = sync_config.get_list('user_groups', True)
        if self.user_groups is None:
            self.user_groups = []
        self.user_groups = self._groupify(self.user_groups)
        self.entitlement_groups = self._groupify(sync_config.get_list('entitlement_groups'))
        self.identity_types = sync_config.get_list('identity_types', True)
        if self.identity_types is None:
            self.identity_types = ['adobeID', 'enterpriseID', 'federatedID']
        connection_config = config_options.get('connection') or {}
        connection_config['ssl_cert_verify'] = config_options.get('ssl_cert_verify')

        # dict w/ structure - umapi_name -> adobe_group -> [set of roles]
        self.admin_roles = self._admin_role_mapping(sync_config)

        sign_orgs = sync_config.get_list('sign_orgs')
        self.clients = {}
        for sign_org_config in sign_orgs:
            sign_org_config['connection'] = connection_config
            sign_client = SignClient(sign_org_config)
            self.clients[sign_client.console_org] = sign_client
        self.test_mode = test_mode

    def run(self, post_sync_data):
        """
        Run the Sign sync
        :param post_sync_data:
        :return:
        """
        if self.test_mode:
            self.logger.info("Sign Sync disabled in test mode")
            return
        for org_name, sign_client in self.clients.items():
            # create any new Sign groups
            for new_group in set(self.user_groups[org_name]) - set(sign_client.sign_groups()):
                self.logger.info("Creating new Sign group: {}".format(new_group))
                sign_client.create_group(new_group)
            umapi_users = post_sync_data.umapi_data.get(org_name)
            if umapi_users is None:
                raise AssertionException("Error getting umapi users from post_sync_data")
            self.update_sign_users(umapi_users, sign_client, org_name)

    def update_sign_users(self, umapi_users, sign_client, org_name):
        sign_users = sign_client.get_users()
        users_update_list = []
        for _, umapi_user in umapi_users.items():
            sign_user = sign_users.get(umapi_user['email'].lower())
            if not self.should_sync(umapi_user, sign_user, org_name):
                continue

            assignment_group = None

            for group in self.user_groups[org_name]:
                if group in umapi_user['groups']:
                    assignment_group = group
                    break

            if assignment_group is None:
                assignment_group = sign_client.DEFAULT_GROUP_NAME

            group_id = sign_client.groups.get(assignment_group)
            admin_roles = self.admin_roles.get(org_name, {})
            user_roles = self.resolve_new_roles(umapi_user, admin_roles)
            user_data = {
                "userId": sign_user['userId'],
                "email": sign_user['email'],
                "firstName": sign_user['firstName'],
                "groupId": group_id,
                "lastName": sign_user['lastName'],
                "roles": user_roles,
            }
            if sign_user['group'].lower() == assignment_group and self.roles_match(user_roles, sign_user['roles']):
                self.logger.debug("skipping Sign update for '{}' -- no updates needed".format(umapi_user['email']))
                continue
            users_update_list.append(user_data)

        # Update in a batch so as to utilize asyncio
        sign_client.update_users(users_update_list)

    @staticmethod
    def roles_match(resolved_roles, sign_roles):
        if isinstance(sign_roles, str):
            sign_roles = [sign_roles]
        return sorted(resolved_roles) == sorted(sign_roles)

    @staticmethod
    def resolve_new_roles(umapi_user, role_mapping):
        roles = set()
        for group in umapi_user['groups']:
            sign_roles = role_mapping.get(group.lower())
            if sign_roles is None:
                continue
            roles.update(sign_roles)
        return list(roles) if roles else ['NORMAL_USER']

    def should_sync(self, umapi_user, sign_user, org_name):
        """
        Initial gatekeeping to determine if user is candidate for Sign sync
        Any checks that don't depend on the Sign record go here
        Sign record must be defined for user, and user must belong to at least one entitlement group
        and user must be accepted identity type
        :param umapi_user:
        :param sign_user:
        :param org_name:
        :return:
        """
        return sign_user is not None and set(umapi_user['groups']) & set(self.entitlement_groups[org_name]) and \
               umapi_user['type'] in self.identity_types

    @staticmethod
    def _groupify(groups):
        processed_groups = defaultdict(list)
        for g in groups:
            processed_group = AdobeGroup.create(g)
            processed_groups[processed_group.umapi_name].append(processed_group.group_name.lower())
        return processed_groups

    @staticmethod
    def _admin_role_mapping(sync_config):
        admin_roles = sync_config.get_list('admin_roles', True)
        if admin_roles is None:
            return {}

        mapped_admin_roles = {}
        for mapping in admin_roles:
            sign_role = mapping.get('sign_role')
            if sign_role is None:
                raise AssertionException("must define a Sign role in admin role mapping")
            adobe_groups = mapping.get('adobe_groups')
            if adobe_groups is None or not len(adobe_groups):
                continue
            for g in adobe_groups:
                group = AdobeGroup.create(g)
                group_name = group.group_name.lower()
                if group.umapi_name not in mapped_admin_roles:
                    mapped_admin_roles[group.umapi_name] = {}
                if group_name not in mapped_admin_roles[group.umapi_name]:
                    mapped_admin_roles[group.umapi_name][group_name] = set()
                mapped_admin_roles[group.umapi_name][group_name].add(sign_role)
        return mapped_admin_roles
