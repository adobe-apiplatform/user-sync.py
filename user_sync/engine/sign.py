import logging
from collections import defaultdict

import six

from user_sync import error
from user_sync.config.common import DictConfig
from user_sync.connector.connector_sign import SignConnector
from user_sync.engine.umapi import AdobeGroup
from user_sync.error import AssertionException


class SignSyncEngine:
    default_options = {
        # based on what's required in sign-sync-config
        'test_mode': False,
        'user_groups': [],
        'entitlement_groups': [],
        'identity_types': [],
        'admin_roles': None,
        'create_users': False,
        'sign_only_limit': 200
    }
    name = 'sign_sync'
    DEFAULT_GROUP_NAME = 'default group'

    def __init__(self, caller_options):
        super().__init__()
        options = dict(self.default_options)
        options.update(caller_options)
        self.options = options
        self.logger = logging.getLogger(self.name)
        self.test_mode = options.get('test_mode')
        sync_config = DictConfig('<%s configuration>' % self.name, caller_options)
        self.user_groups = options['user_groups'] = sync_config.get_list('user_groups', True)
        if self.user_groups is None:
            self.user_groups = []
        self.user_groups = self._groupify(self.user_groups)
        self.entitlement_groups = self._groupify(sync_config.get_list('entitlement_groups'))
        self.identity_types = sync_config.get_list('identity_types', True)
        if self.identity_types is None:
            self.identity_types = ['adobeID', 'enterpriseID', 'federatedID']

        # dict w/ structure - umapi_name -> adobe_group -> [set of roles]
        self.admin_roles = self._admin_role_mapping(sync_config)

        # builder = user_sync.config.common.OptionsBuilder(sync_config)
        # builder.set_string_value('logger_name', self.name)
        # builder.set_bool_value('test_mode', False)
        # options = builder.get_options()

        sign_orgs = sync_config.get_list('sign_orgs')
        self.connectors = {cfg.get('console_org'): SignConnector(cfg) for cfg in sign_orgs}

    def run(self, directory_groups, directory_connector):
        """
        Run the Sign sync
        :param directory_groups:
        :param directory_connector:
        :return:
        """
        if self.test_mode:
            self.logger.info("Sign Sync disabled in test mode")
            return
        directory_users = self.read_desired_user_groups(directory_groups, directory_connector)
        if directory_users is None:
            raise AssertionException("Error getting umapi users from post_sync_data")
        for org_name, sign_connector in self.connectors.items():
            # create any new Sign groups
            for new_group in set(self.user_groups[org_name]) - set(sign_connector.sign_groups()):
                self.logger.info("Creating new Sign group: {}".format(new_group))
                sign_connector.create_group(new_group)
            self.update_sign_users(directory_users, sign_connector, org_name)

    def update_sign_users(self, directory_users, sign_connector, org_name):
        sign_users = sign_connector.get_users()
        for _, directory_user in directory_users.items():
            sign_user = sign_users.get(directory_user['email'])
            if not self.should_sync(directory_user, sign_user, org_name):
                continue

            assignment_group = None

            for group in self.user_groups[org_name]:
                if group in directory_user['groups']:
                    assignment_group = group
                    break

            if assignment_group is None:
                assignment_group = self.DEFAULT_GROUP_NAME

            group_id = sign_connector.get_group(assignment_group)
            admin_roles = self.admin_roles.get(org_name, {})
            user_roles = self.resolve_new_roles(directory_user, admin_roles)
            update_data = {
                "email": sign_user['email'],
                "firstName": sign_user['firstName'],
                "groupId": group_id,
                "lastName": sign_user['lastName'],
                "roles": user_roles,
            }
            if sign_user['group'].lower() == assignment_group and self.roles_match(user_roles, sign_user['roles']):
                self.logger.debug("skipping Sign update for '{}' -- no updates needed".format(directory_user['email']))
                continue
            try:
                sign_connector.update_user(sign_user['userId'], update_data)
                self.logger.info("Updated Sign user '{}', Group: '{}', Roles: {}".format(
                    directory_user['email'], assignment_group, update_data['roles']))
            except AssertionError as e:
                self.logger.error("Error updating user {}".format(e))

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

    def read_desired_user_groups(self, mappings, directory_connector):
        # this is only the first part of the same method in engine/umapi
        # going to make it return the modified directory users list
        self.logger.debug('Building work list...')

        options = self.options
        directory_group_filter = options['directory_group_filter']
        if directory_group_filter is not None:
            directory_group_filter = set(directory_group_filter)
        extended_attributes = options.get('extended_attributes')

        directory_user_by_user_key = self.directory_user_by_user_key

        directory_groups = set(six.iterkeys(mappings)) if self.will_process_groups() else set()
        if directory_group_filter is not None:
            directory_groups.update(directory_group_filter)
        directory_users = directory_connector.load_users_and_groups(groups=directory_groups,
                                                                    extended_attributes=extended_attributes,
                                                                    all_users=directory_group_filter is None)

        for directory_user in directory_users:
            user_key = self.get_directory_user_key(directory_user)
            if not user_key:
                self.logger.warning("Ignoring directory user with empty user key: %s", directory_user)
                continue
            directory_user_by_user_key[user_key] = directory_user

            # if not self.is_directory_user_in_groups(directory_user, directory_group_filter):
            #     continue
            # if not self.is_selected_user_key(user_key):
            #     continue

        return directory_users

    def is_directory_user_in_groups(self, directory_user, groups):
        """
        :type directory_user: dict
        :type groups: set
        :rtype bool
        """
        if groups is None:
            return True
        for directory_user_group in directory_user['groups']:
            if directory_user_group in groups:
                return True
        return False