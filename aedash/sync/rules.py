import csv
import logging

import aedash.sync.connector.dashboard
import aedash.sync.helper

ENTERPRISE_IDENTITY_TYPE = 'enterpriseID'
FEDERATED_IDENTITY_TYPE = 'federatedID'

OWNING_ORGANIZATION_NAME = None

class RuleProcessor(object):
    
    def __init__(self, caller_options):
        '''
        :type caller_options:dict
        '''        
        options = {
            'directory_group_filter': None,
            'username_filter_regex': None,
            
            'new_account_type': ENTERPRISE_IDENTITY_TYPE,
            'manage_groups': True,
            'update_user_info': True,
            
            'remove_user_key_list': None,
            'remove_list_output_path': None,
            'remove_nonexistent_users': False
        }
        options.update(caller_options)        
        self.options = options        
        self.directory_user_by_user_key = {}
        self.filtered_directory_user_by_user_key = {}
        self.organization_info_by_organization = {}
        
        remove_user_key_list = options['remove_user_key_list']
        remove_user_key_list = set(remove_user_key_list) if (remove_user_key_list != None) else set()
        self.remove_user_key_list = remove_user_key_list
        
        self.need_to_find_orphaned_dashboard_users = options['remove_list_output_path'] != None or options['remove_nonexistent_users']
                
        self.logger = logger = logging.getLogger('processor')
        
        if (logger.isEnabledFor(logging.DEBUG)):
            options_to_report = options.copy()
            username_filter_regex = options_to_report['username_filter_regex']
            if (username_filter_regex != None):
                options_to_report['username_filter_regex'] = "%s: %s" % (type(username_filter_regex), username_filter_regex.pattern)
            logger.debug('Initialized with options: %s', options_to_report)
            
    def will_manage_groups(self):
        return self.options['manage_groups']
    
    def get_organization_info(self, organization_name):
        organization_info = self.organization_info_by_organization.get(organization_name)
        if (organization_info == None):
            self.organization_info_by_organization[organization_name] = organization_info = OrganizationInfo(organization_name)
        return organization_info
    
    def read_desired_user_groups(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(Group)
        :type directory_connector: aedash.sync.connector.directory.DirectoryConnector
        '''
        self.logger.info('Building work list...')
        
        for dashboard_groups in mappings.itervalues():
            for dashboard_group in dashboard_groups:
                organization_info = self.get_organization_info(dashboard_group.organization_name)
                organization_info.add_mapped_group(dashboard_group.group_name)
        
        options = self.options
        directory_group_filter = options['directory_group_filter']
        if (directory_group_filter != None):
            directory_group_filter = set(directory_group_filter)
        
        directory_user_by_user_key = self.directory_user_by_user_key        
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key
        remove_user_key_list = self.remove_user_key_list

        directory_groups = set(mappings.iterkeys())
        if (directory_group_filter != None):
            directory_groups.union(directory_group_filter)
        all_loaded, directory_users = directory_connector.load_users_and_groups(directory_groups) 
        if (not all_loaded and self.need_to_find_orphaned_dashboard_users):
            self.logger.warn('Not all users loaded.  Cannot check orphaned users...')
            self.need_to_find_orphaned_dashboard_users = False
        
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
            for group in directory_user['groups']:
                dashboard_groups = mappings.get(group)
                if (dashboard_groups != None):
                    for dashboard_group in dashboard_groups:
                        organization_info = self.get_organization_info(dashboard_group.organization_name)
                        organization_info.add_desired_group_for(user_key, dashboard_group.group_name)
    
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
                    self.add_groups_for_trustee(user_key, trustee_organization_info, desired_groups, dashboard_connector)
                    
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
                    
    def clean_dashboard_users(self, dashboard_connectors):
        '''
        :type dashboard_connectors: DashboardConnectors
        '''
        remove_user_key_list = self.remove_user_key_list
            
        if (self.need_to_find_orphaned_dashboard_users):
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
            
        if (len(remove_user_key_list)):
            self.logger.info('Removing users: %s', remove_user_key_list)
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
                    else:
                        groups_to_remove = mapped_groups

                    if (len(groups_to_remove) > 0):
                        self.logger.info('Removing groups for user key: %s removed: %s', user_key, groups_to_remove)
                        username, domain = self.parse_user_key(user_key)
                        commands = aedash.sync.connector.dashboard.Commands(username, domain)
                        commands.remove_groups(groups_to_remove)
                        dashboard_connector.send_commands(commands)

            organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)
            for user_key in remove_user_key_list:
                if (organization_info.get_dashboard_user(user_key) != None):
                    self.logger.info('Removing user for user key: %s', user_key)
                    username, domain = self.parse_user_key(user_key)
                    commands = aedash.sync.connector.dashboard.Commands(username, domain)
                    commands.remove_from_org()
                    dashboard_connectors.get_owning_connector().send_commands(commands)
     
    def get_user_attributes(self, directory_user):
        attributes = {}
        attributes['email'] = directory_user['email']
        attributes['firstname'] = directory_user['firstname']
        attributes['lastname'] = directory_user['lastname']
        return attributes
            
    def add_dashboard_user(self, user_key, dashboard_connectors):
        '''
        :type user_key: str
        :type dashboard_connectors: DashboardConnectors
        '''
        self.logger.info('Adding user with user key: %s', user_key)

        options = self.options
        default_new_account_type = options['new_account_type']
        update_user_info = options['update_user_info'] 
        manage_groups = self.will_manage_groups()

        directory_user = self.directory_user_by_user_key[user_key]

        attributes = self.get_user_attributes(directory_user)
        country = directory_user['country']
        if (country != None):
            attributes['country'] = country                
        attributes['option'] = "updateIfAlreadyExists" if update_user_info else 'ignoreIfAlreadyExists'
        
        account_type = directory_user.get('identitytype')
        if (account_type == None):
            account_type = default_new_account_type
        
        commands = aedash.sync.connector.dashboard.Commands(directory_user['username'], directory_user['domain'])
        if (account_type == FEDERATED_IDENTITY_TYPE):
            commands.add_federated_user(attributes)
        else:
            commands.add_enterprise_user(attributes)
        if (manage_groups):
            owning_organization_info = self.get_organization_info(OWNING_ORGANIZATION_NAME)
            desired_groups = owning_organization_info.get_desired_groups(user_key)
            groups_to_add = self.calculate_groups_to_add(owning_organization_info, user_key, desired_groups)
            commands.add_groups(groups_to_add)

        def callback(create_action, is_success, error):
            if is_success:
                if (manage_groups):
                    for organization_name, dashboard_connector in dashboard_connectors.trustee_connectors.iteritems():
                        trustee_organization_info = self.get_organization_info(organization_name)
                        desired_groups = trustee_organization_info.get_desired_groups(user_key)
                        self.add_groups_for_trustee(user_key, trustee_organization_info, desired_groups, dashboard_connector)
        dashboard_connectors.get_owning_connector().send_commands(commands, callback)

    def add_groups_for_trustee(self, user_key, organization_info, desired_groups, dashboard_connector):
        '''
        :type user_key: dict
        :type organization_info: OrganizationInfo
        :type desired_groups: set(str)
        :type dashboard_connector: aedash.sync.connector.dashboard.DashboardConnector
        '''
        self.logger.info('Adding groups for user key: %s organization: %s groups: %s', user_key, organization_info.get_name(), desired_groups)
        groups_to_add = self.calculate_groups_to_add(organization_info, user_key, desired_groups)        

        username, domain = self.parse_user_key(user_key)
        commands = aedash.sync.connector.dashboard.Commands(username, domain)
        commands.add_groups(groups_to_add)
        dashboard_connector.send_commands(commands)

    def update_dashboard_users_for_connector(self, organization_info, dashboard_connector):
        '''
        :type organization_info: OrganizationInfo
        :type dashboard_connector: aedash.sync.connector.dashboard.DashboardConnector
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
                groups_to_add = self.calculate_groups_to_add(organization_info, user_key, desired_groups - current_groups)
                groups_to_remove = (current_groups - desired_groups) & organization_info.get_mapped_groups()
                
                if (len(groups_to_add) > 0 or len(groups_to_remove) > 0):
                    self.logger.info('Managing groups for user key: %s added: %s removed: %s', user_key, groups_to_add, groups_to_remove)

            commands = aedash.sync.connector.dashboard.Commands(directory_user['username'], directory_user['domain'])
            commands.update_user(user_attribute_difference)
            commands.add_groups(groups_to_add)
            commands.remove_groups(groups_to_remove)
            dashboard_connector.send_commands(commands)
        
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
                normalized_group_name = aedash.sync.helper.normalize_string(group_name)
                result.add(normalized_group_name)
        return result

    def calculate_groups_to_add(self, organization_info, user_key, desired_groups):
        '''
        :type organization_info: OrganizationInfo
        :type user_key: str
        :type desired_groups: iterator(str) 
        '''
        groups_to_add = None
        if (desired_groups != None):
            groups_added = organization_info.get_groups_added_for(user_key)
            if (groups_added != None):
                groups_to_add = desired_groups - groups_added
                if (self.logger.isEnabledFor(logging.DEBUG)):
                    groups_already_added = desired_groups & groups_added
                    if (len(groups_already_added) > 0):
                        self.logger.debug('Skipped added groups for user: %s groups: %s', user_key, groups_already_added)
            else:
                groups_to_add = desired_groups
            if (len(groups_to_add) > 0):
                organization_info.add_groups_added_for(user_key, groups_to_add)                
        return groups_to_add

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
        username = aedash.sync.helper.normalize_string(username)
        domain = aedash.sync.helper.normalize_string(domain)
        email = aedash.sync.helper.normalize_string(email)

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
        rows = aedash.sync.helper.iter_csv_rows(file_path, 
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
        with open(file_path, 'w', 1) as output_file:
            delimiter = aedash.sync.helper.guess_delimiter_from_filename(file_path)            
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
        :type owning_connector: aedash.sync.connector.dashboard.DashboardConnector
        :type trustee_connectors: dict(str, aedash.sync.connector.dashboard.DashboardConnector)
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
                    action_manager.execute()
                    had_work = True
            if not had_work:
                break
    
class Group(object):
    def __init__(self, group_name, organization_name):
        '''
        :type group_name: str
        :type organization_name: str        
        '''
        self.group_name = group_name
        self.organization_name = organization_name
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(frozenset(self.__dict__))
    
    def __str__(self):
        return str(self.__dict__)
        
class OrganizationInfo(object):
    def __init__(self, name):
        '''
        :type name: str
        '''
        self.name = name
        self.mapped_groups = set()
        self.desired_groups_by_user_key = {}
        self.dashboard_user_by_user_key = {}
        self.orphaned_dashboard_user_by_user_key = {}
        self.groups_added_by_user_key = {}

    def get_name(self):
        return self.name
    
    def add_mapped_group(self, group):
        '''
        :type group: str
        '''
        normalized_group_name = aedash.sync.helper.normalize_string(group)
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
            normalized_group_name = aedash.sync.helper.normalize_string(group)
            desired_groups.add(normalized_group_name)

    def add_dashboard_user(self, user_key, user):
        '''
        :type user_key: str
        :type user: dict
        '''
        self.dashboard_user_by_user_key[user_key] = user
        
    def iter_dashboard_users(self):
        dashboard_user_by_user_key = self.dashboard_user_by_user_key
        return [] if dashboard_user_by_user_key == None else dashboard_user_by_user_key.iteritems()
    
    def get_dashboard_user(self, user_key):
        dashboard_user_by_user_key = self.dashboard_user_by_user_key
        return None if dashboard_user_by_user_key == None else dashboard_user_by_user_key.get(user_key)
    
    def add_orphaned_dashboard_user(self, user_key, user):
        '''
        :type user_key: str
        :type user: dict
        '''
        self.orphaned_dashboard_user_by_user_key[user_key] = user
        
    def iter_orphaned_dashboard_users(self):
        orphaned_dashboard_user_by_user_key = self.orphaned_dashboard_user_by_user_key
        return [] if orphaned_dashboard_user_by_user_key == None else orphaned_dashboard_user_by_user_key.iteritems() 
            
    def get_groups_added_for(self, user_key):
        '''
        :type user_key: str
        '''
        groups_added = self.groups_added_by_user_key.get(user_key)
        return groups_added
        
    def add_groups_added_for(self, user_key, groups):
        '''
        :type user_key: str
        :type groups: iterator(str)
        '''
        groups_added = self.get_groups_added_for(user_key)
        if (groups_added == None):
            self.groups_added_by_user_key[user_key] = groups_added = set()
        groups_added |= groups
        
    def __repr__(self):
        return "OrganizationInfo('name': %s)" % self.name
