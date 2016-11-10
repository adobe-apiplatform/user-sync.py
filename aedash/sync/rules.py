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
            'manage_products': True,
            'update_user_info': True
        }
        options.update(caller_options)        
        self.options = options        
        self.directory_user_by_user_key = {}
        self.desired_products_by_organization = {}
        self.orphaned_dashboard_users_by_organization = {}
        
        self.logger = logger = logging.getLogger('processor')
        logger.debug('Initialized with options: %s', options)
    
    def read_desired_user_products(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(Product)
        :type directory_connector: aedash.sync.connector.directory.DirectoryConnector
        '''
        self.logger.info('Building work list...')
        directory_user_by_user_key = self.directory_user_by_user_key        
        directory_groups = mappings.keys()
        for directory_user in directory_connector.load_users_and_groups(directory_groups):
            user_key = RuleProcessor.get_directory_user_key(directory_user)
            directory_user_by_user_key[user_key] = directory_user            
            self.get_user_desired_products(OWNING_ORGANIZATION_NAME, user_key)                         
            for group in directory_user['groups']:
                dashboard_products = mappings.get(group)
                if (dashboard_products != None):
                    for dashboard_product in dashboard_products:
                        organization_name = dashboard_product.organization_name
                        user_desired_products = self.get_user_desired_products(organization_name, user_key)
                        user_desired_products.add(dashboard_product.product_name)
    
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
        self.logger.info('Synching...')
        
        options = self.options
        manage_products = options['manage_products'] 
        
        added_dashboard_user_keys = set()
        _owning_dashboard_users, owning_orphaned_dashboard_users, owning_unprocessed_products_by_user_key = self.update_dashboard_users_for_connector(OWNING_ORGANIZATION_NAME, dashboard_connectors.get_owning_connector())
        self.orphaned_dashboard_users_by_organization[OWNING_ORGANIZATION_NAME] = owning_orphaned_dashboard_users 
        for user_key in owning_unprocessed_products_by_user_key.iterkeys():
            self.add_dashboard_user(user_key, dashboard_connectors)
            added_dashboard_user_keys.add(user_key)

        for organization_name, dashboard_connector in dashboard_connectors.get_trustee_connectors().iteritems():
            _trustee_dashboard_users, trustee_orphaned_dashboard_users, trustee_unprocessed_products_by_user_key = self.update_dashboard_users_for_connector(organization_name, dashboard_connector)
            self.orphaned_dashboard_users_by_organization[organization_name] = trustee_orphaned_dashboard_users 
            if (manage_products):
                for user_key, desired_products in trustee_unprocessed_products_by_user_key.iteritems():
                    if (user_key in added_dashboard_user_keys):
                        continue
                    directory_user = self.directory_user_by_user_key[user_key]
                    self.add_products_for_connector(directory_user, desired_products, dashboard_connector)
    
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
        attributes['country'] = directory_user['country']                
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
            
            user_attribute_difference = None
            if (update_user_info and organization_name == OWNING_ORGANIZATION_NAME):
                user_attribute_difference = self.get_user_attribute_difference(directory_user, dashboard_user)
            
            products_to_add = None
            products_to_remove = None    
            if (manage_products):                
                desired_products = desired_products_by_user_key.pop(user_key, None)
                if desired_products == None:
                    desired_products = set()
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
        
