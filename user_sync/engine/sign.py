import logging
import time

import six

from user_sync.config.common import DictConfig, ConfigFileLoader, as_set, check_max_limit
from user_sync.connector.connector_sign import SignConnector
from user_sync.error import AssertionException

from sign_client.model import DetailedUserInfo, UserGroupsInfo, UserGroupInfo, DetailedGroupInfo


class SignSyncEngine:
    default_options = {
        'directory_group_filter': None,
        'identity_source': {
            'type': 'ldap',
            'connector': 'connector-ldap.yml'
        },
        'invocation_defaults': {
            'users': 'mapped',
            'test_mode': False
        },
        'sign_orgs': [
            {
                'primary': 'connector-sign.yml'
            }
        ],
        'user_sync': {
            'sign_only_limit': 100,
            'sign_only_user_action': 'reset'
        }
    }

    name = 'sign_sync'
    encoding = 'utf-8'

    def __init__(self, caller_options):
        """
        Initialize the Sign Sync Engine
        :param caller_options:
        :return:
        """
        super().__init__()
        options = dict(self.default_options)
        options.update(caller_options)
        self.options = options
        self.logger = logging.getLogger(self.name)
        sync_config = DictConfig('<%s configuration>' %
                                 self.name, caller_options)
        self.directory_user_by_user_key = {}
        sign_orgs = sync_config.get_dict('sign_orgs')
        connection = sync_config.get_dict('connection')
        self.config_loader = ConfigFileLoader(self.encoding, {}, {})
        self.connectors: dict[str, SignConnector] = {}
        self.default_groups = {}
        self.sign_groups = {}
        # Each of the Sign orgs is captured in a dict with the org name as key
        # and org specific parameter embedded in Sign Connector as value
        for org in sign_orgs:
            self.connectors[org] = SignConnector(
                self.config_loader.load_root_config(sign_orgs[org]), org, options['test_mode'], connection)

        self.action_summary = {}
        self.sign_users_by_org = {}
        self.total_sign_user_count = 0
        self.sign_users_created = set()
        self.sign_users_deactivated = set()
        self.sign_admins_matched = set()
        self.sign_users_matched_groups = set()
        self.sign_users_group_updates = set()
        self.sign_users_role_updates = set()
        self.sign_users_matched_no_updates = set()
        self.directory_users_excluded = set()
        self.sign_only_users_by_org = {}
        self.sign_user_primary_groups = {}
        self.total_sign_only_user_count = 0

    def get_groups(self, org):
        return self.connectors[org].sign_groups()

    def get_default_group(self, org):
        return [g for g in self.connectors[org].sign_groups().values() if g.isDefaultGroup][0]

    def run(self, directory_groups, directory_connector):
        """
        Run the Sign sync
        :param directory_groups:
        :param directory_connector:
        :return:
        """

        for org_name in self.connectors:
            self.sign_groups[org_name] = self.get_groups(org_name)
            self.default_groups[org_name] = self.get_default_group(org_name)

        self.read_desired_user_groups(directory_groups, directory_connector)

        for org_name, sign_connector in self.connectors.items():
            # Create any new Sign groups
            org_directory_groups = self._groupify(
                org_name, directory_groups.values())
            for directory_group in org_directory_groups:
                if (directory_group.lower() not in self.sign_groups[org_name]):
                    self.logger.info(
                        "{}Creating new Sign group: {}".format(self.org_string(org_name), directory_group))
                    sign_connector.create_group(DetailedGroupInfo(name=directory_group))
            self.sign_groups[org_name] = self.get_groups(org_name)
            # Update user details or insert new user
            self.update_sign_users(
                self.directory_user_by_user_key, sign_connector, org_name)
            if org_name in self.sign_only_users_by_org:
                self.handle_sign_only_users(sign_connector, org_name)
        self.log_action_summary()

    def log_action_summary(self):

        self.action_summary = {
            'Number of directory users read': len(self.directory_user_by_user_key),
            'Number of directory selected for input': len(self.directory_user_by_user_key) - len(
                self.directory_users_excluded),
            'Number of directory users excluded': len(self.directory_users_excluded),
            'Number of Sign users read': self.total_sign_user_count,
            'Number of Sign users not in directory (sign-only)': self.total_sign_only_user_count,
            'Number of Sign users updated': len(self.sign_users_group_updates | self.sign_users_role_updates),
            'Number of users with matched groups unchanged': len(self.sign_users_matched_groups),
            'Number of users with admin roles unchanged': len(self.sign_admins_matched),
            'Number of users with groups updated': len(self.sign_users_group_updates),
            'Number of users admin roles updated': len(self.sign_users_role_updates),
            'Number of users matched with no updates': len(self.sign_users_matched_no_updates),
            'Number of Sign users created': len(self.sign_users_created),
            'Number of Sign users deactivated': len(self.sign_users_deactivated),
        }

        pad = max(len(k) for k in self.action_summary)
        header = '------- Action Summary -------'
        self.logger.info('---------------------------' + header + '---------------------------')
        for description, count in self.action_summary.items():
            self.logger.info('  {}: {}'.format(description.rjust(pad, ' '), count))

    def update_sign_users(self, directory_users, sign_connector: SignConnector, org_name):
        """
        Updates user details or inserts new user
        :param directory_groups:
        :param sign_connector:
        :param org_name:
        :return:
        """
        # Fetch the list of active Sign users
        sign_users = sign_connector.get_users()
        sign_user_groups = sign_connector.get_user_groups()
        self.sign_user_primary_groups[org_name] = {id: [g for g in groups if g.isPrimaryGroup][0] for id, groups in sign_user_groups.items()}
        users_update_list = []
        user_groups_update_list = []
        dir_users_for_org = {}
        self.total_sign_user_count += len(sign_users)
        self.sign_users_by_org[org_name] = sign_users
        for _, directory_user in directory_users.items():

            if not self.should_sync(directory_user, org_name):
                continue

            sign_user = sign_users.get(directory_user['email'])
            dir_users_for_org[directory_user['email']] = directory_user
            assignment_group = self.retrieve_assignment_group(directory_user)

            if assignment_group is None:
                assignment_group = self.default_groups[org_name].groupName
            group_id = self.sign_groups[org_name][assignment_group.lower()].groupId
            user_roles = self.retrieve_admin_role(directory_user)
            if sign_user is None:
                # Insert new user if flag is enabled and if Neptune Console
                if sign_connector.create_users:
                    self.insert_new_users(
                        sign_connector, directory_user, user_roles, group_id, assignment_group)
                else:
                    self.logger.info("{0}User {1} not present in  and will be skipped."
                                     .format(self.org_string(org_name), directory_user['email']))
                    self.directory_users_excluded.add(directory_user['email'])
                    continue
            else:
                is_admin = 'ACCOUNT_ADMIN' in user_roles
                # do not update if admin status should not change
                if sign_user.isAccountAdmin != is_admin:
                    # Update existing users
                    if is_admin:
                        self.logger.info(f"Assigning account admin status to {sign_user.email}")
                    else:
                        self.logger.info(f"Removing account admin status from f{sign_user.email}")
                    user_data = DetailedUserInfo(**sign_user.__dict__)
                    user_data.isAccountAdmin = is_admin
                    users_update_list.append(user_data)
                # manage primary group asssignment
                current_group = self.sign_user_primary_groups[org_name][sign_user.id]
                if current_group.name.lower() != assignment_group.lower():
                    assignment_group_info = self.sign_groups[org_name][assignment_group.lower()]
                    self.logger.info(f"Assigning primary group '{assignment_group}' to user {sign_user.email}")
                    group_admin = 'GROUP_ADMIN' in user_roles
                    if group_admin:
                        self.logger.info(f"Assigning Group Admin role to {sign_user.email}")
                    group_update_data = UserGroupsInfo(groupInfoList=[UserGroupInfo(
                        id=assignment_group_info.groupId,
                        isGroupAdmin=group_admin,
                        isPrimaryGroup=True,
                        status='ACTIVE',
                    )])
                    user_groups_update_list.append((sign_user.id, group_update_data))
                
        sign_connector.update_users(users_update_list)
        sign_connector.update_user_groups(user_groups_update_list)
        self.sign_only_users_by_org[org_name] = {}
        for user, data in sign_users.items():
            if user not in dir_users_for_org:
                self.total_sign_only_user_count += 1
                self.sign_only_users_by_org[org_name][user] = data

    @staticmethod
    def roles_match(resolved_roles, sign_roles) -> bool:
        """
        Checks if the existing user role in Sign Console is same as in configuration
        :param resolved_roles:
        :param sign_roles:
        :return:
        """
        return as_set(resolved_roles) == as_set(sign_roles)

    @staticmethod
    def should_sync(directory_user, org_name) -> bool:
        """
        Check if the user belongs to org.  If user has NO groups specified,
        we assume primary and return True (else we cannot assign roles without
        groups)
        :param umapi_user:
        :param org_name:
        :return:
        """
        group = directory_user['sign_group']['group']
        return group.umapi_name == org_name if group else True

    @staticmethod
    def retrieve_assignment_group(directory_user) -> str:
        group = directory_user['sign_group']['group']
        return group.group_name if group else None

    @staticmethod
    def retrieve_admin_role(directory_user) -> list:
        return directory_user['sign_group']['roles']

    @staticmethod
    def _groupify(org_name, groups):
        """
        Extracts the Sign Group name from the configuration for an org
        :param org_name:
        :param groups:
        :return:
        """
        processed_groups = []
        for group_dict in groups:
            for group in group_dict['groups']:
                group_name = group.group_name
                if (org_name == group.umapi_name):
                    processed_groups.append(group_name)
        return processed_groups

    def read_desired_user_groups(self, mappings, directory_connector):
        """
        Reads and loads the users and group information from the identity source
        :param mappings:
        :param directory_connector:
        :return:
        """
        self.logger.debug('Building work list...')

        options = self.options
        directory_group_filter = options['directory_group_filter']
        if directory_group_filter is not None:
            directory_group_filter = set(directory_group_filter)
        directory_user_by_user_key = self.directory_user_by_user_key

        directory_groups = set(six.iterkeys(mappings))
        if directory_group_filter is not None:
            directory_groups.update(directory_group_filter)
        directory_users = directory_connector.load_users_and_groups(groups=directory_groups,
                                                                    extended_attributes=[],
                                                                    all_users=directory_group_filter is None)

        for directory_user in directory_users:
            if not self.is_directory_user_in_groups(directory_user, directory_group_filter):
                continue

            user_key = self.get_directory_user_key(directory_user)
            if not user_key:
                self.logger.warning(
                    "Ignoring directory user with empty user key: %s", directory_user)
                continue
            sign_group = self.extract_mapped_group(directory_user['groups'], mappings)
            directory_user['sign_group'] = sign_group
            directory_user_by_user_key[user_key] = directory_user

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

    def get_directory_user_key(self, directory_user):
        """
        :type directory_user: dict
        """
        email = directory_user.get('email')
        if email:
            return six.text_type(email)
        return None

    @staticmethod
    def extract_mapped_group(directory_user_group, group_mapping) -> dict:

        roles = set()
        matched_group = None

        matched_mappings = {g: m for g, m in group_mapping.items() if g in directory_user_group}
        ordered_mappings = list(matched_mappings.values())
        ordered_mappings.sort(key=lambda x: x['priority'])

        if ordered_mappings is not None:
            groups = []
            for g in ordered_mappings:
                roles |= g['roles']
                if g['groups']:
                    groups.extend(g['groups'])
            if groups:
                matched_group = groups[0]

        # return roles as list instead of set
        sign_group_mapping = {
            'group': matched_group,
            'roles': list(roles) if roles else ['NORMAL_USER']
        }

        # For illustration.  Just return line 322 instead.
        return sign_group_mapping

    def insert_new_users(self, sign_connector, directory_user, user_roles, group_id, assignment_group):
        """
        Constructs the data for insertion and inserts new user in the Sign Console
        :param sign_connector:
        :param directory_user:
        :param user_roles:
        :param group_id:
        :param assignment_group:
        :return:
        """
        insert_data = self.construct_sign_user(directory_user, group_id, user_roles)
        try:
            sign_connector.insert_user(insert_data)
            self.sign_users_created.add(directory_user['email'])
            self.logger.info("{}Inserted sign user '{}', group: '{}', roles: {}".format(
                self.org_string(sign_connector.console_org), directory_user['email'], assignment_group,
                insert_data['roles']))
        except AssertionException as e:
            self.logger.error(format(e))
        return

    def construct_sign_user(self, user, group_id, user_roles):

        user = {k.lower(): u for k, u in user.items()}

        user_data = {
            "email": user['email'],
            "firstName": user['firstname'],
            "groupId": group_id,
            "lastName": user['lastname'],
            "roles": user_roles,
        }
        return user_data

    def handle_sign_only_users(self, sign_connector, org_name):
        """
        Searches users to set to default group in GPS and deactivate in the Sign Neptune console
        :param directory_users:
        :param sign_connector:
        :param sign_user:
        :param org_name:
        :param default_group:
        :return:
        """

        # This will check the limit settings and log a message if the limit is exceeded
        if not self.check_sign_max_limit(org_name):
            return

        sign_only_user_action = self.options['user_sync']['sign_only_user_action']
        users_update_list = []
        groups_update_list = []
        for user in self.sign_only_users_by_org[org_name].values():
            if sign_only_user_action == 'exclude':
                self.logger.debug(
                    f"Sign user '{user.email}' was excluded from sync. sign_only_user_action: set to '{sign_only_user_action}'")
                continue
            elif sign_connector.deactivate_users and sign_only_user_action == 'deactivate':
                try:
                    sign_connector.deactivate_user(user.id)
                    self.logger.info(f"{self.org_string(org_name)}Deactivated sign user '{user.email}'")
                except AssertionException as e:
                    self.logger.error("Error deactivating user {}, {}".format(user['email'], e))
                    continue

            in_default_group = self.sign_user_primary_groups[org_name][user.id].id == self.default_groups[org_name].groupId
            is_group_admin = self.sign_user_primary_groups[org_name][user.id].isGroupAdmin

            if in_default_group and not is_group_admin and not user.isAccountAdmin:
                continue

            # set up group update in case we end up making one
            new_user_group = UserGroupInfo(
                id=self.sign_user_primary_groups[org_name][user.id].id,
                isGroupAdmin=self.sign_user_primary_groups[org_name][user.id].isGroupAdmin,
                isPrimaryGroup=True,
                status='ACTIVE',
            )
            if sign_only_user_action == 'reset':
                new_user_group.id = self.default_groups[org_name].groupId
                new_user_group.isGroupAdmin = False
                self.logger.info(f"{self.org_string(org_name)}Resetting '{user.email}' to Default Group and removing group admin status")
                groups_update_list.append((user.id, UserGroupsInfo(groupInfoList=[new_user_group])))
            if sign_only_user_action == 'remove_roles' and is_group_admin:
                new_user_group.isGroupAdmin = False
                self.logger.info(f"{self.org_string(org_name)}Removing group admin status for user '{user.email}'")
                groups_update_list.append((user.id, UserGroupsInfo(groupInfoList=[new_user_group])))
            if sign_only_user_action == 'remove_groups' and not in_default_group:
                new_user_group.id = self.default_groups[org_name].groupId
                self.logger.info(f"{self.org_string(org_name)}Resetting '{user.email}' to Default Group")
                groups_update_list.append((user.id, UserGroupsInfo(groupInfoList=[new_user_group])))

            # remove admin status if needed
            if sign_only_user_action in ['remove_roles', 'reset'] and user.isAccountAdmin:
                    user_update = DetailedUserInfo(**user.__dict__)
                    user_update.isAccountAdmin = False
                    self.logger.info(f"{self.org_string(org_name)}Removing account admin status for user '{user.email}'")
                    users_update_list.append(user_update)

        sign_connector.update_users(users_update_list)
        sign_connector.update_user_groups(groups_update_list)

    def check_sign_max_limit(self, org_name):
        stray_count = len(self.sign_only_users_by_org[org_name])
        sign_only_limit = self.options['user_sync']['sign_only_limit']
        return check_max_limit(stray_count, sign_only_limit, self.total_sign_user_count, 0, 'Sign', self.logger,
                               self.org_string(org_name))

    def org_string(self, org):
        return "Org: {} - ".format(org.capitalize()) if len(self.connectors) > 1 else ""
