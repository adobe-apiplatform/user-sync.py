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
import user_sync.helper
import user_sync.identity_type

OWNING_ORGANIZATION_NAME = None

class RuleProcessor(object):
    
    def __init__(self, caller_options):
        '''
        :type caller_options:dict
        '''        
        options = {
            'directory_group_filter': None,
            'username_filter_regex': None,
            
            'new_account_type': user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE,
            'manage_groups': True,
            'update_user_info': True,
            
            'remove_user_key_list': None,
            'remove_list_output_path': None,
            'remove_nonexistent_users': False,
            'default_country_code': None,

            'extended_attributes': None,
            'after_mapping_hook': None
        }
        options.update(caller_options)        
        self.options = options        
        self.directory_user_by_user_key = {}
        self.filtered_directory_user_by_user_key = {}
        self.organization_info_by_organization = {}
        self.adding_dashboard_user_key = set()
        
        remove_user_key_list = options['remove_user_key_list']
        remove_user_key_list = set(remove_user_key_list) if (remove_user_key_list != None) else set()
        self.remove_user_key_list = remove_user_key_list
        
        self.need_to_process_orphaned_dashboard_users = options['remove_list_output_path'] != None or options['remove_nonexistent_users']
                
        self.logger = logger = logging.getLogger('processor')
        
        if (logger.isEnabledFor(logging.DEBUG)):
            options_to_report = options.copy()
            username_filter_regex = options_to_report['username_filter_regex']
            if (username_filter_regex != None):
                options_to_report['username_filter_regex'] = "%s: %s" % (type(username_filter_regex), username_filter_regex.pattern)
            logger.debug('Initialized with options: %s', options_to_report)
    
    def run(self, directory_groups, directory_connector, dashboard_connectors):
        '''
        :type directory_groups: dict(str, list(Group)
        :type directory_connector: user_sync.connector.directory.DirectoryConnector
        :type dashboard_connectors: DashboardConnectors
        '''
        logger = self.logger

        self.prepare_organization_infos(directory_groups)

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
            
    def will_manage_groups(self):
        return self.options['manage_groups']
    
    def get_organization_info(self, organization_name):
        organization_info = self.organization_info_by_organization.get(organization_name)
        if (organization_info == None):
            self.organization_info_by_organization[organization_name] = organization_info = OrganizationInfo(organization_name)
        return organization_info
    
    def prepare_organization_infos(self, mappings):
        '''
        :type mappings: dict(str, list(Group)
        '''                   
        for dashboard_groups in mappings.itervalues():
            for dashboard_group in dashboard_groups:
                organization_info = self.get_organization_info(dashboard_group.organization_name)
                organization_info.add_mapped_group(dashboard_group.group_name)

    def read_desired_user_groups(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(Group)
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
        remove_user_key_list = self.remove_user_key_list

        directory_groups = set(mappings.iterkeys())
        if (directory_group_filter != None):
            directory_groups.update(directory_group_filter)
        all_loaded, directory_users = directory_connector.load_users_and_groups(directory_groups, extended_attributes)
        if (not all_loaded and self.need_to_process_orphaned_dashboard_users):
            self.logger.warn('Not all users loaded.  Cannot check orphaned users...')
            self.need_to_process_orphaned_dashboard_users = False
        
        for directory_user in directory_users:
            user_key = RuleProcessor.get_directory_user_key(directory_user)
            directory_user_by_user_key[user_key] = directory_user            
            
            if not self.is_directory_user_in_groups(directory_user, directory_group_filter):
                continue
            if not self.is_selected_user_key(user_key):
                continue
            if (user_key in remove_user_key_list):
                continue
            
            filtered_directory_user_by_user_key[user_key] = directory_user
            self.get_organization_info(OWNING_ORGANIZATION_NAME).add_desired_group_for(user_key, None)

            source_attributes = directory_user['source_attributes'].copy()

            # [TODO morr 2017-02-26]: Need a more robust way to assemble the target attributes
            target_attributes = directory_user.copy()
            target_attributes.pop('groups', None)
            target_attributes.pop('identitytype', None)
            target_attributes.pop('source_attributes', None)

            source_groups = set()
            target_groups = set()

            for group in directory_user['groups']:
                source_groups.add(group) # directory group name
                dashboard_groups = mappings.get(group)
                if (dashboard_groups != None):
                    for dashboard_group in dashboard_groups:
                        target_groups.add(  (dashboard_group.group_name, dashboard_group.organization_name)  )

            self.logger.debug('After-mapping hook point; code would be called with these values...])
            self.logger.debug('  Source attributes: %s', repr(source_attributes))
            self.logger.debug('  Target attributes: %s', repr(target_attributes))
            self.logger.debug('  Source groups: %s', repr(source_groups))
            self.logger.debug('  Target groups: %s', repr(target_groups))

            for target_group_name, target_organization_name in target_groups:
                target_group = Group.get_dashboard_group(target_group_name, target_organization_name)
                if (target_group is not None):
                    organization_info = self.get_organization_info(target_organization_name)
                    organization_info.add_desired_group_for(user_key, target_group_name)
                else:
                    target_group_qualified_name = target_group_name
                    if (target_organization_name is not None):
                        target_group_qualified_name = target_organization_name + '::' + target_group_name
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
        :type dashboard_connectors: DashboardConnectors
        '''        
        manage_groups = self.will_manage_groups()
        
        self.logger.info('Syncing owning...') 
        owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)
        owning_unprocessed_groups_by_user_key = self.update_dashboard_users_for_connector(owning_organization_info, dashboard_connectors.get_owning_connector())
        for user_key in owning_unprocessed_groups_by_user_key.iterkeys():
            self.add_dashboard_user(user_key, dashboard_connectors)

        for organization_name, dashboard_connector in dashboard_connectors.get_trustee_connectors().iteritems():
            self.logger.info('Syncing trustee %s...', organization_name) 
            trustee_organization_info = self.get_organization_info(organization_name)
            if (len(trustee_organization_info.get_mapped_groups()) == 0):
                self.logger.info('No mapped groups for trustee: %s', organization_name) 
                continue

            trustee_unprocessed_groups_by_user_key = self.update_dashboard_users_for_connector(trustee_organization_info, dashboard_connector)
            if (manage_groups):
                for user_key, desired_groups in trustee_unprocessed_groups_by_user_key.iteritems():
                    self.try_and_update_dashboard_user(trustee_organization_info, user_key, dashboard_connector, groups_to_add=desired_groups)
                    
    def iter_orphaned_federated_dashboard_users(self):
        owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)
        for user_key, dashboard_user in owning_organization_info.iter_orphaned_dashboard_users():
            if not self.is_selected_user_key(user_key):
                continue
            if (dashboard_user.get('type') != 'federatedID'):
                continue
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
        remove_user_key_list = self.remove_user_key_list
            
        options = self.options
        remove_list_output_path = options['remove_list_output_path']
        remove_nonexistent_users = options['remove_nonexistent_users']
        
        orphaned_federated_dashboard_users = list(self.iter_orphaned_federated_dashboard_users())
        self.logger.info('Federated orphaned users to be removed: %s', [self.get_dashboard_user_key(dashboard_user) for dashboard_user in orphaned_federated_dashboard_users])        
        
        if (remove_list_output_path != None):
            self.logger.info('Writing remove list to: %s', remove_list_output_path)
            self.write_remove_list(remove_list_output_path, orphaned_federated_dashboard_users)
        elif (remove_nonexistent_users):
            for dashboard_user in orphaned_federated_dashboard_users:
                user_key = self.get_dashboard_user_key(dashboard_user)
                remove_user_key_list.add(user_key)
                    
    def clean_dashboard_users(self, dashboard_connectors):
        '''
        :type dashboard_connectors: DashboardConnectors
        '''
        remove_user_key_list = self.remove_user_key_list
        if (len(remove_user_key_list) == 0):
            return

        owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)
        
        self.logger.info('Removing users: %s', remove_user_key_list)                
        ready_to_remove_from_org = False

        total_waiting_by_user_key = {}
        for user_key in remove_user_key_list:
            total_waiting_by_user_key[user_key] = 0

        def try_and_remove_from_org(user_key):
            total_waiting = total_waiting_by_user_key[user_key]
            if total_waiting == 0:    
                if (not owning_organization_info.is_dashboard_users_loaded() or owning_organization_info.get_dashboard_user(user_key) != None):
                    self.logger.info('Removing user for user key: %s', user_key)
                    username, domain = self.parse_user_key(user_key)
                    commands = user_sync.connector.dashboard.Commands(username=username, domain=domain)
                    commands.remove_from_org()
                    dashboard_connectors.get_owning_connector().send_commands(commands)

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
        
        for organization_name, dashboard_connector in dashboard_connectors.get_trustee_connectors().iteritems():
            organization_info = self.get_organization_info(organization_name)
            mapped_groups = organization_info.get_mapped_groups()
            if (len(mapped_groups) == 0):
                self.logger.info('No mapped groups for trustee: %s', organization_name) 
                continue
                            
            for user_key in remove_user_key_list:
                dashboard_user = organization_info.get_dashboard_user(user_key)
                if (dashboard_user != None):
                    groups_to_remove = self.normalize_groups(dashboard_user.get('groups')) & mapped_groups
                elif not organization_info.is_dashboard_users_loaded():
                    groups_to_remove = mapped_groups
                else:
                    groups_to_remove = None

                if (groups_to_remove != None and len(groups_to_remove) > 0):
                    self.logger.info('Removing groups for user key: %s removed: %s', user_key, groups_to_remove)
                    username, domain = self.parse_user_key(user_key)
                    commands = user_sync.connector.dashboard.Commands(username=username, domain=domain)
                    commands.remove_groups(groups_to_remove)
                    dashboard_connector.send_commands(commands, create_remove_groups_callback(user_key))

        ready_to_remove_from_org = True
        for user_key in remove_user_key_list:
            try_and_remove_from_org(user_key)
     
    def get_user_attributes(self, directory_user):
        attributes = {}
        attributes['email'] = directory_user['email']
        attributes['firstname'] = directory_user['firstname']
        attributes['lastname'] = directory_user['lastname']
        return attributes
    
    def get_identity_type_from_directory_user(self, directory_user):
        identity_type = directory_user.get('identitytype')
        if (identity_type == None):
            identity_type = self.options['new_account_type']
        return identity_type
            
    def create_commands_from_directory_user(self, directory_user, identity_type = None):
        '''
        :type user_key: str
        :type identity_type: str
        :type directory_user: dict
        '''
        if (identity_type == None):
            identity_type = self.get_identity_type_from_directory_user(directory_user)
        commands = user_sync.connector.dashboard.Commands(identity_type, directory_user['email'], directory_user['username'], directory_user['domain'])
        return commands
    
    def add_dashboard_user(self, user_key, dashboard_connectors):
        '''
        Send the action to add a user to the dashboard.  
        After the user is created, the trustees will be updated.
        :type user_key: str
        :type dashboard_connectors: DashboardConnectors
        '''
        self.logger.info('Adding user with user key: %s', user_key)

        options = self.options
        update_user_info = options['update_user_info'] 
        manage_groups = self.will_manage_groups()

        directory_user = self.directory_user_by_user_key[user_key]
        identity_type = self.get_identity_type_from_directory_user(directory_user)
        commands = self.create_commands_from_directory_user(directory_user, identity_type)

        attributes = self.get_user_attributes(directory_user)
        # check whether the country is set in the directory, use default if not
        country = directory_user['country']
        if not country:
            country = options['default_country_code']
        if identity_type == user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE and not country:
            # Enterprise users are allowed to have undefined country
            country = 'UD'
        if (country != None):
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
                if (manage_groups):
                    for organization_name, dashboard_connector in dashboard_connectors.trustee_connectors.iteritems():
                        trustee_organization_info = self.get_organization_info(organization_name)
                        if (trustee_organization_info.get_dashboard_user(user_key) == None):
                            # We manually inject the groups if the dashboard user has not been loaded. 
                            self.calculate_groups_to_add(trustee_organization_info, user_key, trustee_organization_info.get_desired_groups(user_key))
                        
                        trustee_groups_to_add = trustee_organization_info.groups_added_by_user_key.get(user_key)
                        trustee_groups_to_remove = trustee_organization_info.groups_removed_by_user_key.get(user_key)                                                
                        self.update_dashboard_user(trustee_organization_info, user_key, dashboard_connector, groups_to_add=trustee_groups_to_add, groups_to_remove=trustee_groups_to_remove)

        self.adding_dashboard_user_key.add(user_key)
        dashboard_connectors.get_owning_connector().send_commands(commands, callback)

    def update_dashboard_user(self, organization_info, user_key, dashboard_connector, attributes_to_update = None, groups_to_add = None, groups_to_remove = None):
        '''
        Send the action to update aspects of an dashboard user, like info and groups
        :type organization_info: OrganizationInfo
        :type user_key: str
        :type dashboard_connector: user_sync.connector.dashboard.DashboardConnector
        :type attributes_to_update: dict
        :type groups_to_add: set(str)
        :type groups_to_remove: set(str)
        '''        
        if ((groups_to_add and len(groups_to_add) > 0) or (groups_to_remove and len(groups_to_remove) > 0)):
            self.logger.info('Managing groups for user key: %s organization: %s added: %s removed: %s', user_key, organization_info.get_name(), groups_to_add, groups_to_remove)

        directory_user = self.directory_user_by_user_key[user_key]
        commands = self.create_commands_from_directory_user(directory_user)
        commands.update_user(attributes_to_update)
        commands.add_groups(groups_to_add)
        commands.remove_groups(groups_to_remove)
        dashboard_connector.send_commands(commands)

    def try_and_update_dashboard_user(self, organization_info, user_key, dashboard_connector, attributes_to_update = None, groups_to_add = None, groups_to_remove = None):
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
            self.update_dashboard_user(organization_info, user_key, dashboard_connector, attributes_to_update, groups_to_add, groups_to_remove)
        elif (attributes_to_update != None or groups_to_add != None or groups_to_remove != None):
            self.logger.info("Delay user update for user: %s organization: %s", user_key, organization_info.get_name())

    def update_dashboard_users_for_connector(self, organization_info, dashboard_connector):
        '''
        :type organization_info: OrganizationInfo
        :type dashboard_connector: user_sync.connector.dashboard.DashboardConnector
        '''
        directory_user_by_user_key = self.directory_user_by_user_key
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key
        
        desired_groups_by_user_key = organization_info.get_desired_groups_by_user_key()
        desired_groups_by_user_key = {} if desired_groups_by_user_key == None else desired_groups_by_user_key.copy()        
        
        options = self.options
        update_user_info = options['update_user_info']
        manage_groups = self.will_manage_groups() 
        
        for dashboard_user in dashboard_connector.iter_users():
            user_key = RuleProcessor.get_dashboard_user_key(dashboard_user)
            organization_info.add_dashboard_user(user_key, dashboard_user)

            directory_user = directory_user_by_user_key.get(user_key)
            if (directory_user == None):
                organization_info.add_orphaned_dashboard_user(user_key, dashboard_user)
                continue     

            desired_groups = desired_groups_by_user_key.pop(user_key, None)
            if (desired_groups == None):
                if (user_key not in filtered_directory_user_by_user_key):
                    continue
                desired_groups = set()
            
            user_attribute_difference = None
            if (update_user_info and organization_info.get_name() == OWNING_ORGANIZATION_NAME):
                user_attribute_difference = self.get_user_attribute_difference(directory_user, dashboard_user)
                if (len(user_attribute_difference) > 0):
                    self.logger.info('Updating info for user key: %s changes: %s', user_key, user_attribute_difference)
            
            groups_to_add = None
            groups_to_remove = None    
            if (manage_groups):        
                current_groups = self.normalize_groups(dashboard_user.get('groups'))
                groups_to_add = desired_groups - current_groups 
                groups_to_remove =  (current_groups - desired_groups) & organization_info.get_mapped_groups()                

            self.try_and_update_dashboard_user(organization_info, user_key, dashboard_connector, user_attribute_difference, groups_to_add, groups_to_remove)
        
        organization_info.set_dashboard_users_loaded()
        
        return desired_groups_by_user_key
    
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

    @staticmethod
    def get_directory_user_key(directory_user):
        '''
        :type directory_user: dict
        '''
        return RuleProcessor.get_user_key(directory_user['username'], directory_user['domain'], directory_user['email'])
    
    @staticmethod
    def get_dashboard_user_key(dashboard_user):
        '''
        :type dashboard_user: dict
        '''
        return RuleProcessor.get_user_key(None, None, dashboard_user['email'])
    
    @staticmethod
    def get_user_key(username, domain, email):
        username = user_sync.helper.normalize_string(username)
        domain = user_sync.helper.normalize_string(domain)
        email = user_sync.helper.normalize_string(email)

        if (username == None):
            return email
        if (username.find('@') >= 0):
            return username
        return username + ',' + domain
    
    @staticmethod
    def parse_user_key(user_key):
        index = user_key.find(',')
        return (user_key, None) if index < 0 else (user_key[:index], user_key[index + 1:])

    @staticmethod
    def get_username_from_user_key(user_key):
        return RuleProcessor.parse_user_key(user_key)[0]
    
    @staticmethod
    def read_remove_list(file_path, delimiter = None, logger = None):
        '''
        :type file_path: str
        :type delimiter: str
        :type logger: logging.Logger
        '''
        result = []
        
        user_column_name = 'user'
        domain_column_name = 'domain'        
        rows = user_sync.helper.iter_csv_rows(file_path, 
                                                delimiter = delimiter, 
                                                recognized_column_names = [user_column_name, domain_column_name], 
                                                logger = logger)
        for row in rows:
            user = row.get(user_column_name)
            domain = row.get(domain_column_name)
            user_key = RuleProcessor.get_user_key(user, domain, None)
            if (user_key != None):
                result.append(user_key)
        return result
    
    def write_remove_list(self, file_path, dashboard_users):
        total_users = 0
        with open(file_path, 'wb') as output_file:
            delimiter = user_sync.helper.guess_delimiter_from_filename(file_path)            
            writer = csv.DictWriter(output_file, fieldnames = ['user', 'domain'], delimiter = delimiter)
            writer.writeheader()
            for dashboard_user in dashboard_users:
                user_key = self.get_dashboard_user_key(dashboard_user)
                username, domain = self.parse_user_key(user_key)
                writer.writerow({'user': username, 'domain': domain})
                total_users += 1
        self.logger.info('Total users in remove list: %d', total_users)
                
        
class DashboardConnectors(object):
    def __init__(self, owning_connector, trustee_connectors):
        '''
        :type owning_connector: user_sync.connector.dashboard.DashboardConnector
        :type trustee_connectors: dict(str, user_sync.connector.dashboard.DashboardConnector)
        '''
        self.owning_connector = owning_connector
        self.trustee_connectors = trustee_connectors
        
        connectors = [owning_connector]
        connectors.extend(trustee_connectors.itervalues())
        self.connectors = connectors
        
    def get_owning_connector(self):
        return self.owning_connector
    
    def get_trustee_connectors(self):
        return self.trustee_connectors
     
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
    
class Group(object):

    dashboard_groups = {}

    def __init__(self, group_name, organization_name):
        '''
        :type group_name: str
        :type organization_name: str        
        '''
        self.group_name = group_name
        self.organization_name = organization_name
        Group.dashboard_groups[(group_name, organization_name)] = self
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(frozenset(self.__dict__))
    
    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def get_dashboard_group(cls, group_name, organization_name):
        '''
        :type group_name: str
        :type organization_name: str
        '''
        return Group.dashboard_groups.get((group_name, organization_name))

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
