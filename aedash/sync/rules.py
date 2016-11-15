import csv
import logging

from aedash.sync.connector.dashboard import Commands


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
            
            'manage_products': True,
            'update_user_info': True,
            
            'remove_list_delimiter': '\t',
            'remove_user_key_list': None,
            'remove_list_output_path': None,
            'remove_nonexistent_users': False
        }
        options.update(caller_options)        
        self.options = options        
        self.directory_user_by_user_key = {}
        self.filtered_directory_user_by_user_key = {}
        self.desired_products_by_organization = {}
        self.dashboard_users_by_organization = {}
        self.orphaned_dashboard_users_by_organization = {}
        
        remove_user_key_list = options['remove_user_key_list']
        remove_user_key_list = set(remove_user_key_list) if (remove_user_key_list != None) else set()
        self.remove_user_key_list = remove_user_key_list
        
        self.find_orphaned_dashboard_users = options['remove_list_output_path'] != None or options['remove_nonexistent_users']
                
        self.logger = logger = logging.getLogger('processor')
        logger.debug('Initialized with options: %s', options)
    
    def read_desired_user_products(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(Product)
        :type directory_connector: aedash.sync.connector.directory.DirectoryConnector
        '''
        self.logger.info('Building work list...')
        
        options = self.options
        directory_group_filter = options['directory_group_filter']
        if (directory_group_filter != None):
            directory_group_filter = set(directory_group_filter)
        
        directory_user_by_user_key = self.directory_user_by_user_key        
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key
        remove_user_key_list = self.remove_user_key_list

        directory_groups = mappings.keys()
        if (directory_group_filter != None):
            directory_groups.extend(directory_group_filter)
        all_loaded, directory_users = directory_connector.load_users_and_groups(directory_groups) 
        if (not all_loaded and self.find_orphaned_dashboard_users):
            self.logger.warn('Not all users loaded.  Cannot check orphaned users...')
            self.find_orphaned_dashboard_users = False
                                       
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
            self.get_user_desired_products(OWNING_ORGANIZATION_NAME, user_key)                         
            for group in directory_user['groups']:
                dashboard_products = mappings.get(group)
                if (dashboard_products != None):
                    for dashboard_product in dashboard_products:
                        organization_name = dashboard_product.organization_name
                        user_desired_products = self.get_user_desired_products(organization_name, user_key)
                        user_desired_products.add(dashboard_product.product_name)
    
        self.logger.info('Total users after filtering: %d', len(filtered_directory_user_by_user_key))
        self.logger.debug('Product work list: %s', self.desired_products_by_organization)

    
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
    
    def get_user_desired_products(self, organization_name, user_key):
        desired_products_by_organization = self.desired_products_by_organization
        organization_desired_products = desired_products_by_organization.get(organization_name)
        if (organization_desired_products == None):
            desired_products_by_organization[organization_name] = organization_desired_products = {}
        user_desired_products = organization_desired_products.get(user_key)
        if (user_desired_products == None):
            organization_desired_products[user_key] = user_desired_products = set()
        return user_desired_products     
    
    def process_dashboard_users(self, dashboard_connectors):
        '''
        :type dashboard_connectors: DashboardConnectors
        '''        
        options = self.options
        manage_products = options['manage_products'] 
        
        dashboard_users_by_organization = self.dashboard_users_by_organization
        orphaned_dashboard_users_by_organization = self.orphaned_dashboard_users_by_organization
        
        added_dashboard_user_keys = set()

        self.logger.info('Syncing owning...') 
        owning_dashboard_users, owning_orphaned_dashboard_users, owning_unprocessed_products_by_user_key = self.update_dashboard_users_for_connector(OWNING_ORGANIZATION_NAME, dashboard_connectors.get_owning_connector())
        dashboard_users_by_organization[OWNING_ORGANIZATION_NAME] = owning_dashboard_users
        orphaned_dashboard_users_by_organization[OWNING_ORGANIZATION_NAME] = owning_orphaned_dashboard_users 
        for user_key in owning_unprocessed_products_by_user_key.iterkeys():
            self.add_dashboard_user(user_key, dashboard_connectors)
            added_dashboard_user_keys.add(user_key)

        if (self.find_orphaned_dashboard_users or manage_products):
            for organization_name, dashboard_connector in dashboard_connectors.get_trustee_connectors().iteritems():
                self.logger.info('Syncing trustee %s...', organization_name) 
                trustee_dashboard_users, trustee_orphaned_dashboard_users, trustee_unprocessed_products_by_user_key = self.update_dashboard_users_for_connector(organization_name, dashboard_connector)
                dashboard_users_by_organization[organization_name] = trustee_dashboard_users
                orphaned_dashboard_users_by_organization[organization_name] = trustee_orphaned_dashboard_users 
                if (manage_products):
                    for user_key, desired_products in trustee_unprocessed_products_by_user_key.iteritems():
                        if (user_key in added_dashboard_user_keys):
                            continue
                        directory_user = self.directory_user_by_user_key[user_key]
                        self.add_products_for_connector(directory_user, desired_products, dashboard_connector)
                    
    def iter_orphaned_federated_dashboard_users(self):
        owning_orphaned_dashboard_users = self.orphaned_dashboard_users_by_organization[OWNING_ORGANIZATION_NAME]
        for user_key, dashboard_user in owning_orphaned_dashboard_users.iteritems():
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
            
        if (self.find_orphaned_dashboard_users):
            options = self.options
            remove_list_output_path = options['remove_list_output_path']
            remove_nonexistent_users = options['remove_nonexistent_users']
            
            if (remove_list_output_path != None):
                self.logger.info('Writing remove list to: %s', remove_list_output_path)
                self.write_remove_list(remove_list_output_path, self.iter_orphaned_federated_dashboard_users())
            elif (remove_nonexistent_users):
                self.logger.info('Registering federated orphaned users to be removed...')        
                for dashboard_user in self.iter_orphaned_federated_dashboard_users():
                    user_key = self.get_dashboard_user_key(dashboard_user)
                    remove_user_key_list.add(user_key)
            
        if (len(remove_user_key_list)):
            self.logger.info('Removing users: %s', remove_user_key_list)
            dashboard_users_by_organization = self.dashboard_users_by_organization
            for organization_name, dashboard_connector in dashboard_connectors.get_trustee_connectors().iteritems():
                dashboard_users = dashboard_users_by_organization.get(organization_name)
                for user_key in remove_user_key_list:
                    if (dashboard_users == None) or (user_key in dashboard_users):
                        username, domain = self.parse_user_key(user_key)
                        commands = Commands(username, domain)
                        commands.remove_all_products()
                        dashboard_connector.send_commands(commands)

            dashboard_users = dashboard_users_by_organization[OWNING_ORGANIZATION_NAME]
            for user_key in remove_user_key_list:
                if (user_key in dashboard_users):
                    username, domain = self.parse_user_key(user_key)
                    commands = Commands(username, domain)
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
        update_user_info = options['update_user_info'] 
        manage_products = options['manage_products'] 

        directory_user = self.directory_user_by_user_key[user_key]

        attributes = self.get_user_attributes(directory_user)
        country = directory_user['country']
        if (country != None):
            attributes['country'] = country                
        attributes['option'] = "updateIfAlreadyExists" if update_user_info else 'ignoreIfAlreadyExists'
        
        commands = Commands(directory_user['username'], directory_user['domain'])
        commands.add_enterprise_user(attributes)
        if (manage_products):
            desired_products_by_user_key = self.desired_products_by_organization.get(OWNING_ORGANIZATION_NAME)
            if (desired_products_by_user_key != None):
                desired_products = desired_products_by_user_key.get(user_key)
                commands.add_products(desired_products)

        def callback(create_action, is_success, error):
            if is_success:
                if (manage_products):
                    self.add_products_for_trustee_connectors(directory_user, dashboard_connectors.trustee_connectors)
        dashboard_connectors.get_owning_connector().send_commands(commands, callback)

    def add_products_for_trustee_connectors(self, directory_user, trustee_dashboard_connectors):
        '''
        :type directory_user: dict
        :type trustee_dashboard_connectors: dict(str, aedash.sync.connector.dashboard.DashboardConnector)
        '''
        desired_products_by_organization = self.desired_products_by_organization    
        for organization_name, dashboard_connector in trustee_dashboard_connectors.iteritems():
            desired_products_by_user_key = desired_products_by_organization.get(organization_name)
            if desired_products_by_user_key != None:
                user_key = RuleProcessor.get_directory_user_key(directory_user)
                desired_products = desired_products_by_user_key.get(user_key)
                self.add_products_for_connector(directory_user, desired_products, dashboard_connector)

    def add_products_for_connector(self, directory_user, desired_products, dashboard_connector):
        '''
        :type directory_user: dict
        :type desired_products: set(str)
        :type dashboard_connector: aedash.sync.connector.dashboard.DashboardConnector
        '''
        commands = Commands(directory_user['username'], directory_user['domain'])
        commands.add_products(desired_products)
        dashboard_connector.send_commands(commands)
            
    def update_dashboard_users_for_connector(self, organization_name, dashboard_connector):
        '''
        :type organization_name: str
        :type dashboard_connector: aedash.sync.connector.dashboard.DashboardConnector
        '''
        directory_user_by_user_key = self.directory_user_by_user_key
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key
        
        desired_products_by_user_key = self.desired_products_by_organization.get(organization_name)
        desired_products_by_user_key = {} if desired_products_by_user_key == None else desired_products_by_user_key.copy()        
        all_dashboard_users = {}
        orphaned_dashboard_users = {}
        
        options = self.options
        update_user_info = options['update_user_info']
        manage_products = options['manage_products'] 
        
        for dashboard_user in dashboard_connector.iter_users():
            user_key = RuleProcessor.get_dashboard_user_key(dashboard_user)
            all_dashboard_users[user_key] = dashboard_user

            directory_user = directory_user_by_user_key.get(user_key)
            if (directory_user == None):
                orphaned_dashboard_users[user_key] = dashboard_user
                continue     

            desired_products = desired_products_by_user_key.pop(user_key, None)
            if (desired_products == None):
                if (user_key not in filtered_directory_user_by_user_key):
                    continue
                desired_products = set()
            
            user_attribute_difference = None
            if (update_user_info and organization_name == OWNING_ORGANIZATION_NAME):
                user_attribute_difference = self.get_user_attribute_difference(directory_user, dashboard_user)
            
            products_to_add = None
            products_to_remove = None    
            if (manage_products):        
                current_products = dashboard_user.get('groups')
                current_products = set() if current_products == None else set(current_products)            

                products_to_add = desired_products - current_products
                products_to_remove = current_products - desired_products

            commands = Commands(directory_user['username'], directory_user['domain'])
            commands.update_user(user_attribute_difference)
            commands.add_products(products_to_add)
            commands.remove_products(products_to_remove)
            dashboard_connector.send_commands(commands)
                
        return (all_dashboard_users, orphaned_dashboard_users, desired_products_by_user_key)
    
    def get_user_attribute_difference(self, directory_user, dashboard_user):
        differences = {}
        attributes = self.get_user_attributes(directory_user)
        for key, value in attributes.iteritems():
            dashboard_value = dashboard_user.get(key)
            if (value != dashboard_value):
                differences[key] = value
        return differences        

    @staticmethod
    def normalize_string(string_value):
        '''
        :type string_value: str
        '''
        return string_value.strip().lower() if string_value != None else None
    
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
        username = RuleProcessor.normalize_string(username)
        domain = RuleProcessor.normalize_string(domain)
        email = RuleProcessor.normalize_string(email)

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
    def read_remove_list(file_path, delimiter):
        '''
        :type file_path: str
        :type delimiter: str
        '''
        result = []
        with open(file_path, 'r', 1) as input_file:
            reader = csv.DictReader(input_file, delimiter = delimiter)
            for row in reader:
                user = row.get('user')
                domain = row.get('domain')
                user_key = RuleProcessor.get_user_key(user, domain, None)
                if (user_key != None):
                    result.append(user_key)
        return result
    
    def write_remove_list(self, file_path, dashboard_users):
        options = self.options
        
        total_users = 0
        with open(file_path, 'w', 1) as output_file:                
            writer = csv.DictWriter(output_file, fieldnames = ['user', 'domain'], delimiter = options['remove_list_delimiter'])
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
    
class Product(object):
    def __init__(self, product_name, organization_name):
        '''
        :type product_name: str
        :type organization_name: str        
        '''
        self.product_name = product_name
        self.organization_name = organization_name
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(frozenset(self.__dict__))
    
    def __str__(self):
        return str(self.__dict__)
        
