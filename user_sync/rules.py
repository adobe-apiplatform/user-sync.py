# Copyright (c) 2016-2017 Adobe Systems Incorporated.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import csv
import logging

import user_sync.connector.dashboard
import user_sync.error
import user_sync.helper
import user_sync.identity_type

GROUP_NAME_DELIMITER = '::'
OWNING_ORGANIZATION_NAME = None

class RuleProcessor(object):
    
    def __init__(self, caller_options):
        '''
        :type caller_options:dict
        '''        
        options = {
            # these are in alphabetical order!  Always add new ones that way!
            'after_mapping_hook': None,
            'default_country_code': None,
            'delete_list_output_path': None,
            'delete_nonexistent_users': False,
            'delete_user_key_list': None,
            'directory_group_filter': None,
            'directory_group_mapped': False,
            'exclude_groups': [],
            'exclude_identity_types': [],
            'exclude_users': [],
            'extended_attributes': None,
            'manage_groups': False,
            'max_deletions_per_run': None,
            'max_missing_users': None,
            'new_account_type': user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE,
            'remove_list_output_path': None,
            'remove_nonexistent_users': False,
            'remove_user_key_list': None,
            'update_user_info': True,
            'username_filter_regex': None,
        }
        options.update(caller_options)        
        self.options = options        
        self.directory_user_by_user_key = {}
        self.filtered_directory_user_by_user_key = {}
        self.organization_info_by_organization = {}
        self.adding_dashboard_user_key = set()
        # adobe user-keys to find the number of unique adobe users for action summary log
        self.adobe_users = set()
        # counters for action summary log
        self.action_summary = {
            'total_number_of_adobe_users': 0,
            'number_of_adobe_users_excluded': 0,
            'total_number_of_directory_users': 0,
            'number_of_directory_users_selected': 0,
            'number_of_users_created': 0,
            'number_of_users_updated': 0,
            'number_of_users_with_updated_groups': 0,
            'number_of_users_removed_from_mapped_group': 0,
            'number_of_users_removed': 0,
            'number_of_users_deleted': 0,
            'number_of_users_with_no_changes': 0,
        }

        # save away the exclude options for use in filtering
        self.exclude_groups = self.normalize_groups(options['exclude_groups'])
        self.exclude_identity_types = options['exclude_identity_types']
        self.exclude_users = options['exclude_users']
        # remember users we excluded in the owning org, so when they
        # reappear in later orgs we will exclude them again.
        # TODO: change the way multiple orgs are handled to iterate users only once
        self.excluded_user_keys = set()

        # we only need a reference to either the remove or delete key list,
        # since you can't do both
        self.orphan_user_key_list = set(options['remove_user_key_list'] or options['delete_user_key_list'] or [])
        self.orphan_list_output_path = options['remove_list_output_path'] or options['delete_list_output_path']
        
        # determine if we need to delete user accounts instead of just removing
        # them
        self.delete_user_accounts = options['delete_nonexistent_users'] or options['delete_user_key_list']
        
        # determine whether we need to process orphaned users at all
        self.need_to_process_orphaned_dashboard_users = (
            options['remove_list_output_path'] or options['remove_nonexistent_users'] or
            options['delete_list_output_path'] or options['delete_nonexistent_users']
        )
        
        self.logger = logger = logging.getLogger('processor')

        # in/out variables for per-user after-mapping-hook code
        self.after_mapping_hook_scope = {
            'source_attributes': None,          # in: attributes retrieved from customer directory system (eg 'c', 'givenName')
                                                # out: N/A
            'source_groups': None,              # in: customer-side directory groups found for user
                                                # out: N/A
            'target_attributes': None,          # in: user's attributes for UMAPI calls as defined by usual rules (eg 'country', 'firstname')
                                                # out: user's attributes for UMAPI calls as potentially changed by hook code
            'target_groups': None,              # in: Adobe-side dashboard groups mapped for user by usual rules
                                                # out: Adobe-side dashboard groups as potentially changed by hook code
            'logger': logger,                   # make loging available to hook code
            'hook_storage': None,               # for exclusive use by hook code; persists across calls
        }

        if (logger.isEnabledFor(logging.DEBUG)):
            options_to_report = options.copy()
            username_filter_regex = options_to_report['username_filter_regex']
            if (username_filter_regex != None):
                options_to_report['username_filter_regex'] = "%s: %s" % (type(username_filter_regex), username_filter_regex.pattern)
            logger.debug('Initialized with options: %s', options_to_report)

    def run(self, directory_groups, directory_connector, dashboard_connectors):
        '''
        :type directory_groups: dict(str, list(DashboardGroup)
        :type directory_connector: user_sync.connector.directory.DirectoryConnector
        :type dashboard_connectors: DashboardConnectors
        '''
        logger = self.logger

        self.prepare_organization_infos()

        if (directory_connector != None):
            load_directory_stats = user_sync.helper.JobStats("Load from Directory", divider = "-")
            load_directory_stats.log_start(logger)
            self.read_desired_user_groups(directory_groups, directory_connector)
            load_directory_stats.log_end(logger)
            should_sync_dashboard_users = True
        else:
            should_sync_dashboard_users = False
        
        dashboard_stats = user_sync.helper.JobStats("Sync Dashboard", divider = "-")
        dashboard_stats.log_start(logger)
        if (should_sync_dashboard_users):
            self.process_dashboard_users(dashboard_connectors)
            if self.need_to_process_orphaned_dashboard_users:
                self.process_orphaned_dashboard_users()                            
        self.clean_dashboard_users(dashboard_connectors)    
        dashboard_connectors.execute_actions()
        dashboard_stats.log_end(logger)
        self.log_action_summary()
            
    def log_action_summary(self):
        '''
        log number of directory and Adobe users, number of created / updated / deleted users, and number of users with updated groups
        or removed from mapped group because they were not in directory
        :return: None
        '''
        logger = self.logger
        # find the total number of directory users and selected/filtered users
        self.action_summary['total_number_of_directory_users'] = len(self.directory_user_by_user_key)
        self.action_summary['number_of_directory_users_selected'] = len(self.filtered_directory_user_by_user_key)
        # find the total number of adobe users and excluded users
        self.action_summary['total_number_of_adobe_users'] = len(self.adobe_users)
        self.action_summary['number_of_adobe_users_excluded'] = len(self.excluded_user_keys)
        # find out the number of users that have no changes
        self.action_summary['number_of_users_with_no_changes'] = self.action_summary['total_number_of_adobe_users'] - self.action_summary['number_of_users_updated'] - self.action_summary['number_of_users_removed'] - self.action_summary['number_of_users_deleted']
        logger.info('------------- Action Summary -------------')
        for action_name, action_count in self.action_summary.iteritems():
            logger.info('  %s: %s', action_name, action_count)
        logger.info('------------------------------------------')

    def will_manage_groups(self):
        return self.options['manage_groups']
    
    def get_organization_info(self, organization_name):
        organization_info = self.organization_info_by_organization.get(organization_name)
        if (organization_info == None):
            self.organization_info_by_organization[organization_name] = organization_info = OrganizationInfo(organization_name)
        return organization_info
    
    def prepare_organization_infos(self):
        '''
        Make sure we have prepared organizations for all the mapped groups, including extensions
        '''                   
        for dashboard_group in DashboardGroup.iter_groups():
            organization_info = self.get_organization_info(dashboard_group.get_organization_name())
            organization_info.add_mapped_group(dashboard_group.get_group_name())

    def read_desired_user_groups(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(DashboardGroup))
        :type directory_connector: user_sync.connector.directory.DirectoryConnector
        '''
        self.logger.info('Building work list...')
                
        options = self.options
        directory_group_filter = options['directory_group_filter']
        if (directory_group_filter != None):
            directory_group_filter = set(directory_group_filter)
        extended_attributes = options.get('extended_attributes')
        
        directory_user_by_user_key = self.directory_user_by_user_key        
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key
        orphan_user_key_list = self.orphan_user_key_list

        directory_groups = set(mappings.iterkeys())
        if (directory_group_filter != None):
            directory_groups.update(directory_group_filter)
        all_loaded, directory_users = directory_connector.load_users_and_groups(directory_groups, extended_attributes)
        if (not all_loaded and self.need_to_process_orphaned_dashboard_users):
            self.logger.warn('Not all users loaded.  Cannot check orphaned users...')
            self.need_to_process_orphaned_dashboard_users = False
        
        for directory_user in directory_users:
            user_key = self.get_directory_user_key(directory_user)
            directory_user_by_user_key[user_key] = directory_user            
            
            if not self.is_directory_user_in_groups(directory_user, directory_group_filter):
                continue
            if not self.is_selected_user_key(user_key):
                continue
            if user_key in orphan_user_key_list:
                continue
            
            filtered_directory_user_by_user_key[user_key] = directory_user
            self.get_organization_info(OWNING_ORGANIZATION_NAME).add_desired_group_for(user_key, None)

            # set up groups in hook scope; the target groups will be used whether or not there's customer hook code
            self.after_mapping_hook_scope['source_groups'] = set()
            self.after_mapping_hook_scope['target_groups'] = set()
            for group in directory_user['groups']:
                self.after_mapping_hook_scope['source_groups'].add(group) # this is a directory group name
                dashboard_groups = mappings.get(group)
                if dashboard_groups is not None:
                    for dashboard_group in dashboard_groups:
                        self.after_mapping_hook_scope['target_groups'].add(dashboard_group.get_qualified_name())

            # only if there actually is hook code: set up rest of hook scope, invoke hook, update user attributes
            if options['after_mapping_hook'] is not None:
                self.after_mapping_hook_scope['source_attributes'] = directory_user['source_attributes'].copy()

                target_attributes = dict()
                target_attributes['email'] = directory_user.get('email')
                target_attributes['username'] = directory_user.get('username')
                target_attributes['domain'] = directory_user.get('domain')
                target_attributes['firstname'] = directory_user.get('firstname')
                target_attributes['lastname'] = directory_user.get('lastname')
                target_attributes['country'] = directory_user.get('country')
                target_attributes['uid'] = directory_user.get('uid')
                self.after_mapping_hook_scope['target_attributes'] = target_attributes

                # invoke the customer's hook code
                self.log_after_mapping_hook_scope(before_call=True)
                exec(options['after_mapping_hook'], self.after_mapping_hook_scope)
                self.log_after_mapping_hook_scope(after_call=True)

                # copy modified attributes back to the user object
                directory_user.update(self.after_mapping_hook_scope['target_attributes'])

            for target_group_qualified_name in self.after_mapping_hook_scope['target_groups']:
                target_group = DashboardGroup.lookup(target_group_qualified_name)
                if (target_group is not None):
                    organization_info = self.get_organization_info(target_group.get_organization_name())
                    organization_info.add_desired_group_for(user_key, target_group.get_group_name())
                else:
                    self.logger.error('Target dashboard group %s is not known; ignored', target_group_qualified_name)

        self.logger.info('Total directory users after filtering: %d', len(filtered_directory_user_by_user_key))
        if (self.logger.isEnabledFor(logging.DEBUG)):        
            self.logger.debug('Group work list: %s', dict([(organization_name, organization_info.get_desired_groups_by_user_key()) for organization_name, organization_info in self.organization_info_by_organization.iteritems()]))
    
    def is_directory_user_in_groups(self, directory_user, groups):
        '''
        :type directory_user: dict
        :type groups: set
        :rtype bool
        '''
        if groups == None:
            return True
        for directory_user_group in directory_user['groups']:
            if (directory_user_group in groups):
                return True
        return False
    
    def process_dashboard_users(self, dashboard_connectors):
        '''
        This is where we actually "do the sync"; that is, where we match users on the two sides.
        When we get here, we have loaded all the directory users *and* we have loaded all the dashboard users,
        and (conceptually) we match them up, updating the dashboard users that match, marking the dashboard
        users that don't match for deletion, and adding dashboard users for the directory users that didn't match.
        What makes the code here more complex is that, instead of looping over users just once and
        updating each user in all of the dashboard connectors at that time, we instead loop over users
        once per org for which we have a dashboard connector, and we do the matching logic for each of
        those orgs.
        :type dashboard_connectors: DashboardConnectors
        '''        
        manage_groups = self.will_manage_groups()
        
        self.logger.info('Syncing owning...') 
        owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)

        # Loop over users and compare then and process differences
        owning_unprocessed_groups_by_user_key = self.update_dashboard_users_for_connector(owning_organization_info, dashboard_connectors.get_owning_connector())

        # Handle creates for new users.  This also drives adding the new user to groups in other organizations.
        for user_key in owning_unprocessed_groups_by_user_key.iterkeys():
            self.add_dashboard_user(user_key, dashboard_connectors)

        for organization_name, dashboard_connector in dashboard_connectors.get_accessor_connectors().iteritems():
            self.logger.info('Syncing accessor %s...', organization_name) 
            accessor_organization_info = self.get_organization_info(organization_name)
            if (len(accessor_organization_info.get_mapped_groups()) == 0):
                self.logger.info('No mapped groups for accessor: %s', organization_name) 
                continue

            accessor_unprocessed_groups_by_user_key = self.update_dashboard_users_for_connector(accessor_organization_info, dashboard_connector)
            if (manage_groups):
                for user_key, desired_groups in accessor_unprocessed_groups_by_user_key.iteritems():
                    self.try_and_update_dashboard_user(accessor_organization_info, user_key, dashboard_connector, groups_to_add=desired_groups)
                    
    def iter_orphaned_dashboard_users(self):
        owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)
        for _, dashboard_user in owning_organization_info.iter_orphaned_dashboard_users():
            yield dashboard_user

    def is_selected_user_key(self, user_key):
        '''
        :type user_key: str
        '''
        username_filter_regex = self.options['username_filter_regex']
        if (username_filter_regex != None):
            username = RuleProcessor.get_username_from_user_key(user_key)
            search_result = username_filter_regex.search(username)
            if (search_result == None):
                return False
        return True
    
    def process_orphaned_dashboard_users(self):
        orphan_user_key_list = self.orphan_user_key_list
            
        options = self.options
        orphan_list_output_path = self.orphan_list_output_path
        remove_nonexistent_users = options['remove_nonexistent_users']
        delete_nonexistent_users = options['delete_nonexistent_users']
        
        max_deletions_per_run = options['max_deletions_per_run']
        max_missing_users = options['max_missing_users']

        orphaned_dashboard_users = list(self.iter_orphaned_dashboard_users())
        self.logger.info('Orphaned users to be processed: %s',
                         [self.get_dashboard_user_key(dashboard_user) for dashboard_user in orphaned_dashboard_users])
        
        number_of_orphaned_dashboard_users = len(orphaned_dashboard_users)

        if orphan_list_output_path:
            self.logger.info('Writing orphaned users list to: %s', orphan_list_output_path)
            self.write_orphan_list(orphan_list_output_path, orphaned_dashboard_users)
        elif remove_nonexistent_users or delete_nonexistent_users:
            if number_of_orphaned_dashboard_users > max_missing_users:
                raise user_sync.error.AssertionException(
                    'Unable to process orphaned users, as their count (%s) is larger than max_missing_users setting' %
                    number_of_orphaned_dashboard_users)
            orphan_count = 0
            for dashboard_user in orphaned_dashboard_users:
                orphan_count += 1
                if orphan_count > max_deletions_per_run:
                    self.logger.critical('Only processing %d of the %d orphaned users ' +
                                         'due to max_deletions_per_run setting', max_deletions_per_run,
                                         number_of_orphaned_dashboard_users)
                    break
                user_key = self.get_dashboard_user_key(dashboard_user)
                orphan_user_key_list.add(user_key)
                    
    def clean_dashboard_users(self, dashboard_connectors):
        '''
        Process removal of users.  The list of users to remove is generated earlier in processing.
        :type dashboard_connectors: DashboardConnectors
        '''
        orphan_user_key_list = self.orphan_user_key_list
        if (len(orphan_user_key_list) == 0):
            return

        owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)
        
        self.logger.info('Removing users: %s', orphan_user_key_list)                
        ready_to_remove_from_org = False

        total_waiting_by_user_key = {}
        for user_key in orphan_user_key_list:
            total_waiting_by_user_key[user_key] = 0

        def try_and_remove_from_org(user_key):
            total_waiting = total_waiting_by_user_key[user_key]
            if total_waiting == 0:    
                if (not owning_organization_info.is_dashboard_users_loaded() or owning_organization_info.get_dashboard_user(user_key) != None):
                    self.logger.info('Removing user for user key: %s', user_key)
                    id_type, username, domain = self.parse_user_key(user_key)
                    commands = user_sync.connector.dashboard.Commands(identity_type=id_type,
                                                                      username=username, domain=domain)
                    commands.remove_from_org(self.delete_user_accounts)
                    dashboard_connectors.get_owning_connector().send_commands(commands)
                    # increment removed count or deleted count for action summary
                    if self.delete_user_accounts and user_key in self.delete_user_accounts:
                        self.action_summary['number_of_users_deleted'] += 1
                    else:
                        self.action_summary['number_of_users_removed'] += 1

        def on_remove_groups_callback(user_key):
            total_waiting = total_waiting_by_user_key[user_key]     
            total_waiting -= 1
            total_waiting_by_user_key[user_key] = total_waiting
            if ready_to_remove_from_org:
                try_and_remove_from_org(user_key)

        def create_remove_groups_callback(user_key):
            total_waiting = total_waiting_by_user_key[user_key]     
            total_waiting += 1
            total_waiting_by_user_key[user_key] = total_waiting
            return lambda response: on_remove_groups_callback(user_key)
        
        for organization_name, dashboard_connector in dashboard_connectors.get_accessor_connectors().iteritems():
            organization_info = self.get_organization_info(organization_name)
            mapped_groups = organization_info.get_mapped_groups()
            if (len(mapped_groups) == 0):
                self.logger.info('No mapped groups for accessor: %s', organization_name) 
                continue
                            
            for user_key in orphan_user_key_list:
                dashboard_user = organization_info.get_dashboard_user(user_key)
                if (dashboard_user != None):
                    groups_to_remove = self.normalize_groups(dashboard_user.get('groups')) & mapped_groups
                elif not organization_info.is_dashboard_users_loaded():
                    groups_to_remove = mapped_groups
                else:
                    groups_to_remove = None

                if (groups_to_remove != None and len(groups_to_remove) > 0):
                    self.logger.info('Removing groups for user key: %s removed: %s', user_key, groups_to_remove)
                    id_type, username, domain = self.parse_user_key(user_key)
                    commands = user_sync.connector.dashboard.Commands(identity_type=id_type,
                                                                      username=username, domain=domain)
                    commands.remove_groups(groups_to_remove)
                    dashboard_connector.send_commands(commands, create_remove_groups_callback(user_key))

        ready_to_remove_from_org = True
        for user_key in orphan_user_key_list:
            try_and_remove_from_org(user_key)
     
    def get_user_attributes(self, directory_user):
        attributes = {}
        attributes['email'] = directory_user['email']
        attributes['firstname'] = directory_user['firstname']
        attributes['lastname'] = directory_user['lastname']
        return attributes
    
    def get_identity_type_from_directory_user(self, directory_user):
        identity_type = directory_user.get('identity_type')
        if (identity_type == None):
            identity_type = self.options['new_account_type']
            self.logger.warning('Found user with no identity type, using %s: %s', identity_type, directory_user)
        return identity_type

    def get_identity_type_from_dashboard_user(self, dashboard_user):
        identity_type = dashboard_user.get('type')
        if (identity_type == None):
            identity_type = self.options['new_account_type']
            self.logger.error('Found dashboard user with no identity type, using %s: %s', identity_type, dashboard_user)
        return identity_type

    def create_commands_from_directory_user(self, directory_user, identity_type = None):
        '''
        :type user_key: str
        :type identity_type: str
        :type directory_user: dict
        '''
        if (identity_type == None):
            identity_type = self.get_identity_type_from_directory_user(directory_user)
        commands = user_sync.connector.dashboard.Commands(identity_type, directory_user['email'],
                                                          directory_user['username'], directory_user['domain'])
        return commands
    
    def add_dashboard_user(self, user_key, dashboard_connectors):
        '''
        Send the action to add a user to the dashboard.  
        After the user is created, the accessors will be updated.
        :type user_key: str
        :type dashboard_connectors: DashboardConnectors
        '''
        # Check to see what we're updating
        options = self.options
        update_user_info = options['update_user_info'] 
        manage_groups = self.will_manage_groups()

        # start the add process
        self.logger.info('Adding directory user to Adobe: %s', user_key)
        directory_user = self.directory_user_by_user_key[user_key]
        identity_type = self.get_identity_type_from_directory_user(directory_user)
        commands = self.create_commands_from_directory_user(directory_user, identity_type)
        attributes = self.get_user_attributes(directory_user)
        # check whether the country is set in the directory, use default if not
        country = directory_user['country']
        if not country:
            country = options['default_country_code']
        if not country:
            if identity_type == user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE:
                # Enterprise users are allowed to have undefined country
                country = 'UD'
            else:
                self.logger.error("User %s cannot be added as it has a blank country code and no default has been specified.", user_key)
                return
        attributes['country'] = country
        if (attributes.get('firstname') == None):
            attributes.pop('firstname', None)
        if (attributes.get('lastname') == None):
            attributes.pop('lastname', None)
        attributes['option'] = "updateIfAlreadyExists" if update_user_info else 'ignoreIfAlreadyExists'
        
        commands.add_user(attributes)
        if (manage_groups):
            owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)        
            desired_groups = owning_organization_info.get_desired_groups(user_key)
            groups_to_add = self.calculate_groups_to_add(owning_organization_info, user_key, desired_groups)
            commands.add_groups(groups_to_add)

        def callback(response):
            self.adding_dashboard_user_key.discard(user_key)
            is_success = response.get("is_success")            
            if is_success:
                # increment counter for user created for action summary log
                self.action_summary['number_of_users_created'] += 1
                if (manage_groups):
                    for organization_name, dashboard_connector in dashboard_connectors.accessor_connectors.iteritems():
                        accessor_organization_info = self.get_organization_info(organization_name)
                        if (accessor_organization_info.get_dashboard_user(user_key) == None):
                            # We manually inject the groups if the dashboard user has not been loaded. 
                            self.calculate_groups_to_add(accessor_organization_info, user_key, accessor_organization_info.get_desired_groups(user_key))
                        
                        accessor_groups_to_add = accessor_organization_info.groups_added_by_user_key.get(user_key)
                        accessor_groups_to_remove = accessor_organization_info.groups_removed_by_user_key.get(user_key)                                                
                        self.update_dashboard_user(accessor_organization_info, user_key, dashboard_connector, groups_to_add=accessor_groups_to_add, groups_to_remove=accessor_groups_to_remove)

        self.adding_dashboard_user_key.add(user_key)
        dashboard_connectors.get_owning_connector().send_commands(commands, callback)

    def update_dashboard_user(self, organization_info, user_key, dashboard_connector, attributes_to_update = None, groups_to_add = None, groups_to_remove = None, dashboard_user = None):
        # Note that the user may exist only in the directory, only in the dashboard, or both at this point.
        # When we are updating an Adobe user who has been removed from the directory, we have to be careful to use
        # data from the dashboard_user parameter and not try to get information from the directory.
        '''
        Send the action to update aspects of an dashboard user, like info and groups
        :type organization_info: OrganizationInfo
        :type user_key: str
        :type dashboard_connector: user_sync.connector.dashboard.DashboardConnector
        :type attributes_to_update: dict
        :type groups_to_add: set(str)
        :type groups_to_remove: set(str)
        :type dashboard_user: dict # with type, username, domain, and email entries
        '''        
        if ((groups_to_add and len(groups_to_add) > 0) or (groups_to_remove and len(groups_to_remove) > 0)):
            self.logger.info('Managing groups for user key: %s organization: %s added: %s removed: %s', user_key, organization_info.get_name(), groups_to_add, groups_to_remove)

        if user_key in self.directory_user_by_user_key:
            directory_user = self.directory_user_by_user_key[user_key]
            identity_type = self.get_identity_type_from_directory_user(directory_user)
        else:
            directory_user = dashboard_user
            identity_type = dashboard_user.get('type')

        commands = self.create_commands_from_directory_user(directory_user, identity_type=identity_type)
        if identity_type != user_sync.identity_type.ADOBEID_IDENTITY_TYPE:
            commands.update_user(attributes_to_update)
        else:
            if attributes_to_update and len(attributes_to_update) > 0:
                self.logger.warning("Can't update attributes on Adobe ID user: %s", dashboard_user.get("email"))
        commands.add_groups(groups_to_add)
        commands.remove_groups(groups_to_remove)
        dashboard_connector.send_commands(commands)

        # increment counts if needed for user_updated, user_with_updated_group, and user_removed_from_mapped_group for action summay
        if attributes_to_update and len(attributes_to_update) > 0:
            self.action_summary['number_of_users_updated'] += 1
        if groups_to_add and len(groups_to_add) > 0:
            self.action_summary['number_of_users_with_updated_groups'] += 1
        if groups_to_remove and len(groups_to_remove) > 0:
            self.action_summary['number_of_users_removed_from_mapped_group'] += 1

    def try_and_update_dashboard_user(self, organization_info, user_key, dashboard_connector, attributes_to_update = None, groups_to_add = None, groups_to_remove = None, dashboard_user = None):
        '''
        Send the user update action smartly.   
        If the user is being added, the action is postponed.  
        If a group is already added or removed, the group is excluded.
        :type organization_info: OrganizationInfo
        :type user_key: str
        :type dashboard_connector: user_sync.connector.dashboard.DashboardConnector
        :type attributes_to_update: dict
        :type groups_to_add: set(str)
        :type groups_to_remove: set(str)
        '''        
        groups_to_add = self.calculate_groups_to_add(organization_info, user_key, groups_to_add) 
        groups_to_remove = self.calculate_groups_to_remove(organization_info, user_key, groups_to_remove)
        if (user_key not in self.adding_dashboard_user_key):
            self.update_dashboard_user(organization_info, user_key, dashboard_connector, attributes_to_update, groups_to_add, groups_to_remove, dashboard_user)
        elif (attributes_to_update != None or groups_to_add != None or groups_to_remove != None):
            self.logger.info("Delay user update for user: %s organization: %s", user_key, organization_info.get_name())

    def update_dashboard_users_for_connector(self, organization_info, dashboard_connector):
        '''
        This is the main function that goes over dashboard users and looks for and processes differences.
        It is called with a particular organization that it should manage groups against.
        It returns a map from user keys to dashboard groups:
            the keys are the user keys of all the selected directory users that don't exist in the target dashboard;
            the value for each key is the set of dashboard groups in this org that the created user should be put into.
        The use of this return value by the caller is to create the user and add him to the right groups.
        :type organization_info: OrganizationInfo
        :type dashboard_connector: user_sync.connector.dashboard.DashboardConnector
        :rtype: map(string, set)
        '''
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key

        # the way we construct the return vaue is to start with a map from all directory users
        # to their groups in this org, make a copy, and pop off any dashboard users we find.
        # That way, and key/value pairs left in the map are the unmatched dashboard users and their groups.
        user_to_group_map = organization_info.get_desired_groups_by_user_key()
        user_to_group_map = {} if user_to_group_map == None else user_to_group_map.copy()

        # check to see if we should update dashboard users, and which ones are excluded
        options = self.options
        update_user_info = options['update_user_info']
        manage_groups = self.will_manage_groups()
        exclude_identity_types = self.options['exclude_identity_types']
        will_process_orphans = self.need_to_process_orphaned_dashboard_users

        # there are certain operations we only do in the owning org
        in_owning_org = organization_info.get_name() == OWNING_ORGANIZATION_NAME

        # we only log excluded users if we would have updated them.
        log_excluded_users = update_user_info or manage_groups or will_process_orphans


        # Walk all the dashboard users, getting their group data, matching them with directory users,
        # and adjusting their attribute and group data accordingly.
        for dashboard_user in dashboard_connector.iter_users():
            # get the basic data about this user; initialize change markers to "no change"
            user_key = self.get_dashboard_user_key(dashboard_user)
            organization_info.add_dashboard_user(user_key, dashboard_user)
            attribute_differences = {}
            current_groups = self.normalize_groups(dashboard_user.get('groups'))
            groups_to_add = set()
            groups_to_remove = set()
            # add adobe user to set for action summary
            self.adobe_users.add(user_key)

            # If this dashboard user matches any directory user, pop them out of the
            # map because we know they don't need to be created.
            # Also, keep track of the mapped groups for the directory user
            # so we can update the dashboard user's groups as needed.
            desired_groups = user_to_group_map.pop(user_key, None) or set()

            # check for excluded users
            if self.is_dashboard_user_excluded(in_owning_org, user_key, current_groups, log_excluded_users):
                continue

            directory_user = filtered_directory_user_by_user_key.get(user_key)
            if directory_user is None:
                # There's no selected directory user matching this dashboard user,
                # so we mark this dashboard user as an orphan, and we mark him
                # for removal from any mapped groups.
                if will_process_orphans:
                    organization_info.add_orphaned_dashboard_user(user_key, dashboard_user)
                self.logger.info("Adobe user not in input user set: %s", user_key)
                if manage_groups:
                    groups_to_remove = current_groups & organization_info.get_mapped_groups()
                    if len(groups_to_remove) > 0:
                        self.logger.info("Removed from Groups: %s", groups_to_remove)
            else:
                # There is a selected directory user who matches this dashboard user,
                # so mark any changed dashboard attributes,
                # and mark him for addition and removal of the appropriate mapped groups
                if update_user_info and in_owning_org:
                    attribute_differences = self.get_user_attribute_difference(directory_user, dashboard_user)
                    if (len(attribute_differences) > 0):
                        self.logger.info('Updating info for user key: %s changes: %s', user_key, attribute_differences)
                if manage_groups:
                    groups_to_add = desired_groups - current_groups
                    if len(groups_to_add) > 0:
                        self.logger.info("Added to Groups: %s", groups_to_add)
                    groups_to_remove =  (current_groups - desired_groups) & organization_info.get_mapped_groups()
                    if len(groups_to_remove) > 0:
                        self.logger.info("Removed from Groups: %s", groups_to_remove)

            # Finally, execute the attribute and group adjustments
            self.try_and_update_dashboard_user(organization_info, user_key, dashboard_connector, attribute_differences, groups_to_add, groups_to_remove, dashboard_user)

        # mark the org's dashboard users as processed and return the remaining ones in the map
        organization_info.set_dashboard_users_loaded()
        return user_to_group_map

    def is_dashboard_user_excluded(self, in_owning_org, user_key, current_groups, do_logging):
        if in_owning_org:
            # in the owning org, we actually check the exclusion conditions
            identity_type, username, domain = self.parse_user_key(user_key)
            if identity_type in self.exclude_identity_types:
                if do_logging:
                    self.logger.info("Excluding dashboard user (due to type): %s", user_key)
                self.excluded_user_keys.add(user_key)
                return True
            if len(current_groups & self.exclude_groups) > 0:
                if do_logging:
                    self.logger.info("Excluding dashboard user (due to group): %s", user_key)
                self.excluded_user_keys.add(user_key)
                return True
            for re in self.exclude_users:
                if re.match(username):
                    if do_logging:
                        self.logger.info("Excluding dashboard user (due to name): %s", user_key)
                    self.excluded_user_keys.add(user_key)
                    return True
            return False
        else:
            # in all other orgs, we use the cache, and don't log,
            # because the owning org always gets processed first
            return user_key in self.excluded_user_keys

    @staticmethod
    def normalize_groups(group_names):
        '''
        :type group_name: iterator(str)
        :rtype set(str)
        '''
        result = set()
        if (group_names != None):
            for group_name in group_names:
                normalized_group_name = user_sync.helper.normalize_string(group_name)
                result.add(normalized_group_name)
        return result

    def calculate_groups_to_add(self, organization_info, user_key, desired_groups):
        '''
        Return a set of groups that have not been registered to be added.
        :type organization_info: OrganizationInfo
        :type user_key: str
        :type desired_groups: set(str) 
        '''
        groups_to_add = self.get_new_groups(organization_info.groups_added_by_user_key, user_key, desired_groups)
        if (desired_groups != None and self.logger.isEnabledFor(logging.DEBUG)):
            groups_already_added = desired_groups - groups_to_add
            if (len(groups_already_added) > 0):
                self.logger.debug('Skipped added groups for user: %s groups: %s', user_key, groups_already_added)
        return groups_to_add

    def calculate_groups_to_remove(self, organization_info, user_key, desired_groups):
        '''
        Return a set of groups that have not been registered to be removed.
        :type organization_info: OrganizationInfo
        :type user_key: str
        :type desired_groups: set(str) 
        '''
        groups_to_remove = self.get_new_groups(organization_info.groups_removed_by_user_key, user_key, desired_groups)
        if (desired_groups != None and self.logger.isEnabledFor(logging.DEBUG)):
            groups_already_removed = desired_groups - groups_to_remove
            if (len(groups_already_removed) > 0):
                self.logger.debug('Skipped removed groups for user: %s groups: %s', user_key, groups_already_removed)
        return groups_to_remove

    def get_new_groups(self, current_groups_by_user_key, user_key, desired_groups):
        '''
        Return a set of groups that have not been registered in the dictionary for the specified user.        
        :type current_groups_by_user_key: dict(str, set(str))
        :type user_key: str
        :type desired_groups: set(str) 
        '''
        new_groups = None
        if (desired_groups != None):
            current_groups = current_groups_by_user_key.get(user_key)
            if (current_groups != None):
                new_groups = desired_groups - current_groups
            else:
                new_groups = desired_groups
            if (len(new_groups) > 0):
                if (current_groups == None):
                    current_groups_by_user_key[user_key] = current_groups = set()
                current_groups |= new_groups
        return new_groups


    def get_user_attribute_difference(self, directory_user, dashboard_user):
        differences = {}
        attributes = self.get_user_attributes(directory_user)
        for key, value in attributes.iteritems():
            dashboard_value = dashboard_user.get(key)
            if (value != dashboard_value):
                differences[key] = value
        return differences        

    def get_directory_user_key(self, directory_user):
        '''
        Identity-type aware user key management for directory users
        :type directory_user: dict
        '''
        id_type = self.get_identity_type_from_directory_user(directory_user)
        return self.get_user_key(directory_user['username'], directory_user['domain'], directory_user['email'], id_type)
    
    def get_dashboard_user_key(self, dashboard_user):
        '''
        Identity-type aware user key management for dashboard users
        :type dashboard_user: dict
        '''
        id_type = self.get_identity_type_from_dashboard_user(dashboard_user)
        return self.get_user_key(dashboard_user['username'], dashboard_user['domain'], dashboard_user['email'], id_type)

    @staticmethod
    def get_user_key(username, domain, email, id_type):
        '''
        Construct the user key for a directory or dashboard user.
        The user key is the stringification of the tuple (id_type, username, domain)
        but the domain part is left empty if the username is an email address.
        If the parameters are invalid, None is returned.
        :param username: (required) username of the user, can be his email
        :param domain: (optional) domain of the user
        :param email: (optional) email of the user
        :param id_type: (required) id_type of the user
        :return: string "id_type,username,domain" (or None)
        '''
        id_type = user_sync.identity_type.parse_identity_type(id_type)
        email = user_sync.helper.normalize_string(email)
        username = user_sync.helper.normalize_string(username) or email
        domain = user_sync.helper.normalize_string(domain)

        if not id_type:
            return None
        if not username:
            return None
        if (username.find('@') >= 0):
            domain = ""
        elif not domain:
            return None
        return id_type + ',' + username + ',' + domain
    
    @staticmethod
    def parse_user_key(user_key):
        '''Returns the identity_type, username, and domain for the user.
        The domain part is empty except if the username is not an email address.
        :rtype: tuple
        '''
        return user_key.split(',')

    @staticmethod
    def get_username_from_user_key(user_key):
        return RuleProcessor.parse_user_key(user_key)[1]
    
    @staticmethod
    def read_remove_list(file_path, delimiter = None, logger = None):
        '''
        Load the users to be removed from a CSV file.  Returns the list of user keys.
        :type file_path: str
        :type delimiter: str
        :type logger: logging.Logger
        '''
        result = []

        id_type_column_name = 'type'
        user_column_name = 'user'
        domain_column_name = 'domain'        
        rows = user_sync.helper.iter_csv_rows(file_path,
                                              delimiter = delimiter,
                                              recognized_column_names = [id_type_column_name,
                                                                         user_column_name,
                                                                         domain_column_name],
                                              logger = logger)
        for row in rows:
            id_type = row.get(id_type_column_name)
            user = row.get(user_column_name)
            domain = row.get(domain_column_name)
            
            # specifying None for (optional) email, because we don't have it
            user_key = RuleProcessor.get_user_key(user, domain, None, id_type)
            if user_key:
                result.append(user_key)
            elif logger:
                logger.error("Invalid input line, ignored: %s", row)
        return result

    def write_orphan_list(self, file_path, dashboard_users):
        total_users = 0
        with open(file_path, 'wb') as output_file:
            delimiter = user_sync.helper.guess_delimiter_from_filename(file_path)            
            writer = csv.DictWriter(output_file, fieldnames = ['type', 'user', 'domain'], delimiter = delimiter)
            writer.writeheader()
            for dashboard_user in dashboard_users:
                user_key = self.get_dashboard_user_key(dashboard_user)
                id_type, username, domain = self.parse_user_key(user_key)
                writer.writerow({'type': id_type, 'user': username, 'domain': domain})
                total_users += 1
        self.logger.info('Total users in orphan list: %d', total_users)
            
    def log_after_mapping_hook_scope(self, before_call=None, after_call=None):
        if ((before_call is None and after_call is None) or (before_call is not None and after_call is not None)):
            raise ValueError("Exactly one of 'before_call', 'after_call' must be passed (and not None)")
        when = 'before' if before_call is not None else 'after'
        if (before_call is not None):
            self.logger.debug('.')
            self.logger.debug('Source attrs, %s: %s', when, self.after_mapping_hook_scope['source_attributes'])
            self.logger.debug('Source groups, %s: %s', when, self.after_mapping_hook_scope['source_groups'])
        self.logger.debug('Target attrs, %s: %s', when, self.after_mapping_hook_scope['target_attributes'])
        self.logger.debug('Target groups, %s: %s', when, self.after_mapping_hook_scope['target_groups'])
        if (after_call is not None):
            self.logger.debug('Hook storage, %s: %s', when, self.after_mapping_hook_scope['hook_storage'])


class DashboardConnectors(object):
    def __init__(self, owning_connector, accessor_connectors):
        '''
        :type owning_connector: user_sync.connector.dashboard.DashboardConnector
        :type accessor_connectors: dict(str, user_sync.connector.dashboard.DashboardConnector)
        '''
        self.owning_connector = owning_connector
        self.accessor_connectors = accessor_connectors
        
        connectors = [owning_connector]
        connectors.extend(accessor_connectors.itervalues())
        self.connectors = connectors
        
    def get_owning_connector(self):
        return self.owning_connector
    
    def get_accessor_connectors(self):
        return self.accessor_connectors
     
    def execute_actions(self):
        while True:
            had_work = False
            for connector in self.connectors:
                action_manager = connector.get_action_manager()
                if action_manager.has_work():
                    action_manager.flush()
                    had_work = True
            if not had_work:
                break
    
class DashboardGroup(object):

    index_map = {}

    def __init__(self, group_name, organization_name):
        '''
        :type group_name: str
        :type organization_name: str
        '''
        self.group_name = group_name
        self.organization_name = organization_name
        DashboardGroup.index_map[(group_name, organization_name)] = self
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(frozenset(self.__dict__))
    
    def __str__(self):
        return str(self.__dict__)

    def get_qualified_name(self):
        prefix = ""
        if (self.organization_name is not None and self.organization_name != OWNING_ORGANIZATION_NAME):
            prefix = self.organization_name + GROUP_NAME_DELIMITER
        return prefix + self.group_name

    def get_organization_name(self):
        return self.organization_name

    def get_group_name(self):
        return self.group_name

    @staticmethod
    def _parse(qualified_name):
        '''
        :type qualified_name: str
        :rtype: str, str
        '''
        parts = qualified_name.split(GROUP_NAME_DELIMITER)
        group_name = parts.pop()
        organization_name = GROUP_NAME_DELIMITER.join(parts)
        if (len(organization_name) == 0):
            organization_name = OWNING_ORGANIZATION_NAME
        return group_name, organization_name

    @classmethod
    def lookup(cls, qualified_name):
        return cls.index_map.get(cls._parse(qualified_name))

    @classmethod
    def create(cls, qualified_name):
        group_name, organization_name = cls._parse(qualified_name)
        existing = cls.index_map.get((group_name, organization_name))
        if existing:
            return existing
        elif len(group_name) > 0:
            return cls(group_name, organization_name)
        else:
            return None

    @classmethod
    def iter_groups(cls):
        return cls.index_map.itervalues()


class OrganizationInfo(object):
    def __init__(self, name):
        '''
        :type name: str
        '''
        self.name = name
        self.mapped_groups = set()
        self.desired_groups_by_user_key = {}
        self.dashboard_user_by_user_key = {}
        self.dashboard_users_loaded = False
        self.orphaned_dashboard_user_by_user_key = {}
        self.groups_added_by_user_key = {}
        self.groups_removed_by_user_key = {}

    def get_name(self):
        return self.name
    
    def add_mapped_group(self, group):
        '''
        :type group: str
        '''
        normalized_group_name = user_sync.helper.normalize_string(group)
        self.mapped_groups.add(normalized_group_name)

    def get_mapped_groups(self):
        return self.mapped_groups
    
    def get_desired_groups_by_user_key(self):
        return self.desired_groups_by_user_key

    def get_desired_groups(self, user_key):
        '''
        :type user_key: str
        '''
        desired_groups = self.desired_groups_by_user_key.get(user_key)
        return desired_groups     

    def add_desired_group_for(self, user_key, group):
        '''
        :type user_key: str
        :type group: str
        '''
        desired_groups = self.get_desired_groups(user_key)
        if (desired_groups == None):
            self.desired_groups_by_user_key[user_key] = desired_groups = set()
        if (group != None):
            normalized_group_name = user_sync.helper.normalize_string(group)
            desired_groups.add(normalized_group_name)

    def add_dashboard_user(self, user_key, user):
        '''
        :type user_key: str
        :type user: dict
        '''
        self.dashboard_user_by_user_key[user_key] = user
        
    def iter_dashboard_users(self):
        return self.dashboard_user_by_user_key.iteritems()
    
    def get_dashboard_user(self, user_key):
        '''
        :type user_key: str
        '''
        return self.dashboard_user_by_user_key.get(user_key)
    
    def set_dashboard_users_loaded(self):
        self.dashboard_users_loaded = True
        
    def is_dashboard_users_loaded(self):
        return self.dashboard_users_loaded
    
    def add_orphaned_dashboard_user(self, user_key, user):
        '''
        :type user_key: str
        :type user: dict
        '''
        self.orphaned_dashboard_user_by_user_key[user_key] = user
        
    def iter_orphaned_dashboard_users(self):
        orphaned_dashboard_user_by_user_key = self.orphaned_dashboard_user_by_user_key
        return [] if orphaned_dashboard_user_by_user_key == None else orphaned_dashboard_user_by_user_key.iteritems() 
            
    def __repr__(self):
        return "OrganizationInfo('name': %s)" % self.name
