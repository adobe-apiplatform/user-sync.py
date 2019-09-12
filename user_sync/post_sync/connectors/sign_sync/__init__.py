import logging
from collections import defaultdict
from user_sync.post_sync import PostSyncConnector
from user_sync.config import DictConfig, OptionsBuilder
from user_sync.rules import AdobeGroup
from .client import SignClient


class SignConnector(PostSyncConnector):
    name = 'sign_sync'

    def __init__(self, config_options):
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

        sign_orgs = sync_config.get_list('sign_orgs')
        self.clients = {}
        for sign_org_config in sign_orgs:
            sign_client = SignClient(sign_org_config)
            self.clients[sign_client.console_org] = sign_client

    def run(self, post_sync_data):
        """
        Run the Sign sync
        :param post_sync_data:
        :return:
        """
        for org_name, sign_client in self.clients.items():
            # create any new Sign groups
            for new_group in set(self.user_groups[org_name]) - set(sign_client.groups):
                self.logger.info("Creating new Sign group: {}".format(new_group))
                sign_client.create_group(new_group)
            umapi_users = post_sync_data.umapi_data.get(org_name)
            assert umapi_users is not None, "Error getting umapi users from post_sync_data"
            self.update_sign_users(umapi_users, sign_client, org_name)

    def update_sign_users(self, umapi_users, sign_client, org_name):
        sign_users = sign_client.get_users()
        for _, umapi_user in umapi_users.items():
            sign_user = sign_users.get(umapi_user['email'])
            if not self.should_sync(umapi_user, sign_user, org_name):
                continue

            common_groups = set(self.user_groups[org_name]) & set(umapi_user['groups'])

            if not common_groups:
                continue

            assignment_group = sorted(list(common_groups))[0]
            group_id = sign_client.groups.get(assignment_group)
            user_roles = self.resolve_new_roles(umapi_user, self.entitlement_groups[org_name], assignment_group)
            update_data = {
                "email": umapi_user['email'],
                "firstName": umapi_user['firstname'],
                "groupId": group_id,
                "lastName": umapi_user['lastname'],
                "roles": user_roles,
            }
            if sign_user['group'] == assignment_group and sorted(sign_user['roles']) == sorted(user_roles):
                self.logger.debug("skipping Sign update for '{}' -- no updates needed".format(umapi_user['email']))
                continue
            try:
                sign_client.update_user(sign_user['userId'], update_data)
            except AssertionError as e:
                self.logger.error("Error updating user {}".format(e))
                return
            self.logger.info("Updated Sign user '{}', Group: '{}', Roles: {}".format(
                umapi_user['email'], assignment_group, update_data['roles']))

    @staticmethod
    def resolve_new_roles(umapi_user, entitlement_groups, user_group):
        admin_groups = ['_admin_'+g for g in entitlement_groups]
        admin_user_group = '_admin_'+user_group

        group_admin = bool(set(admin_groups) & set(umapi_user['groups']))
        account_admin = admin_user_group in umapi_user['groups']

        if account_admin and group_admin:
            return ["ACCOUNT_ADMIN", "GROUP_ADMIN"]
        if account_admin:
            return ["ACCOUNT_ADMIN"]
        if group_admin:
            return ["GROUP_ADMIN"]
        return ['NORMAL_USER']

    def should_sync(self, umapi_user, sign_user, org_name):
        """
        Initial gatekeeping to determine if user is candidate for Sign sync
        Sign record must be defined for user, and user must belong to at least one entitlement group
        :param umapi_user:
        :param sign_user:
        :param org_name:
        :return:
        """
        return sign_user is not None and set(umapi_user['groups']) & set(self.entitlement_groups[org_name])

    @staticmethod
    def _groupify(groups):
        processed_groups = defaultdict(list)
        for g in groups:
            processed_group = AdobeGroup.create(g)
            processed_groups[processed_group.umapi_name].append(processed_group.group_name)
        return processed_groups
