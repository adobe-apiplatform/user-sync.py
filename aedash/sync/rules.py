from aedash.sync.connector.dashboard import Commands

ENTERPRISE_IDENTITY_TYPE = 'enterpriseID'
FEDERATED_IDENTITY_TYPE = 'federatedID'

MAIN_ORGANIZATION_NAME = None

class RuleProcessor(object):
    
    def __init__(self, options):
        self.options = options        
        self.directory_user_by_email = {}
        self.desired_products_by_organization = {}
        self.orphaned_dashboard_users_by_organization = {}
    
    def read_desired_user_products(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(Product)
        :type directory_connector: aedash.sync.connector.directory.DirectoryConnector
        '''
        directory_user_by_email = self.directory_user_by_email
        desired_products_by_organization = self.desired_products_by_organization
        
        directory_groups = mappings.keys()
        for directory_user in directory_connector.load_users_and_groups(directory_groups):
            email = RuleProcessor.normalize_email(directory_user['email'])
            directory_user_by_email[email] = directory_user             
            for group in directory_user['groups']:
                dashboard_products = mappings.get(group)
                if (dashboard_products != None):
                    for dashboard_product in dashboard_products:
                        organization_name = dashboard_product.organization_name
                        organization_desired_products = desired_products_by_organization.get(organization_name)
                        if (organization_desired_products == None):
                            desired_products_by_organization[organization_name] = organization_desired_products = {}
                        user_desired_products = organization_desired_products.get(email)
                        if (user_desired_products == None):
                            organization_desired_products[email] = user_desired_products = set()
                        user_desired_products.add(dashboard_product.product_name)
        
    def process_dashboard_users(self, dashboard_connectors):
        '''
        :type dashboard_connectors: DashboardConnectors
        '''
        added_dashboard_emails = set()

        main_dashboard_users, main_orphaned_dashboard_users, main_unprocessed_products_by_email = self.update_dashboard_users_for_connector(MAIN_ORGANIZATION_NAME, dashboard_connectors.get_main_connector())
        self.orphaned_dashboard_users_by_organization[MAIN_ORGANIZATION_NAME] = main_orphaned_dashboard_users 
        for email in main_unprocessed_products_by_email.iterkeys():
            self.add_dashboard_user(email, dashboard_connectors)
            added_dashboard_emails.add(email)

        for organization_name, dashboard_connector in dashboard_connectors.get_trusted_connectors().iteritems():
            _trusted_dashboard_users, trusted_orphaned_dashboard_users, trusted_unprocessed_products_by_email = self.update_dashboard_users_for_connector(organization_name, dashboard_connector)
            self.orphaned_dashboard_users_by_organization[organization_name] = trusted_orphaned_dashboard_users 
            for email, desired_products in trusted_unprocessed_products_by_email.iteritems():
                if (email in added_dashboard_emails):
                    continue
                if (email in main_dashboard_users):
                    directory_user = self.directory_user_by_email[email]
                    self.add_products_for_connector(directory_user, desired_products, dashboard_connector)
                else:
                    self.add_dashboard_user(email, dashboard_connectors)
                    added_dashboard_emails.add(email)
            
    def add_dashboard_user(self, email, dashboard_connectors):
        '''
        :type email: str
        :type dashboard_connectors: DashboardConnectors
        '''
        directory_user = self.directory_user_by_email[email]

        attributes = {}
        attributes['email'] = email
        attributes['firstname'] = directory_user['firstname']
        attributes['lastname'] = directory_user['lastname']
        attributes['country'] = directory_user['country']
        
        commands = Commands(directory_user['username'], directory_user['domain'])
        commands.add_enterprise_user(attributes)
        desired_products_by_email = self.desired_products_by_organization.get(MAIN_ORGANIZATION_NAME)
        if (desired_products_by_email != None):
            desired_products = desired_products_by_email.get(email)
            commands.add_products(desired_products)

        def callback(create_action, is_success, error):
            if is_success:
                self.add_products_for_trusted_connectors(directory_user, dashboard_connectors.trusted_connectors)
        dashboard_connectors.get_main_connector().send_commands(commands, callback)

    def add_products_for_trusted_connectors(self, directory_user, trusted_dashboard_connectors):
        '''
        :type directory_user: dict
        :type trusted_dashboard_connectors: dict(str, aedash.sync.connector.dashboard.DashboardConnector)
        '''
        desired_products_by_organization = self.desired_products_by_organization    
        for organization_name, dashboard_connector in trusted_dashboard_connectors.iteritems():
            desired_products_by_email = desired_products_by_organization.get(organization_name)
            if desired_products_by_email != None:
                desired_products = desired_products_by_email.get(directory_user['email'])
                self.add_products_for_connector(directory_user, desired_products, dashboard_connector)

    def add_products_for_connector(self, directory_user, desired_products, dashboard_connector):
        '''
        :type directory_user: dict
        :type desired_products: set(str)
        :type trusted_dashboard_connectors: dict(str, aedash.sync.connector.dashboard.DashboardConnector)
        '''
        commands = Commands(directory_user['username'], directory_user['domain'])
        commands.add_products(desired_products)
        dashboard_connector.send_commands(commands)
            
    def update_dashboard_users_for_connector(self, organization_name, dashboard_connector):
        '''
        :type organization_name: str
        :type dashboard_connector: aedash.sync.connector.dashboard.DashboardConnector
        '''
        directory_user_by_email = self.directory_user_by_email
        
        desired_products_by_email = self.desired_products_by_organization.get(organization_name)
        desired_products_by_email = {} if desired_products_by_email == None else desired_products_by_email.copy()        
        all_dashboard_users = {}
        orphaned_dashboard_users = {}
        
        for dashboard_user in dashboard_connector.iter_users():
            email = RuleProcessor.normalize_email(dashboard_user['email'])
            all_dashboard_users[email] = dashboard_user
            
            directory_user = directory_user_by_email.get(email)
            if (directory_user == None):
                orphaned_dashboard_users[email] = dashboard_user
                continue                    
                
            desired_products = desired_products_by_email.pop(email, None)
            if desired_products == None:
                desired_products = set()
            current_products = dashboard_user.get('groups')
            current_products = set() if current_products == None else set(current_products)
            
            products_to_add = desired_products - current_products
            products_to_remove = current_products - desired_products

            commands = Commands(directory_user['username'], directory_user['domain'])
            commands.add_products(products_to_add)
            commands.remove_products(products_to_remove)
            dashboard_connector.send_commands(commands)
                
        return (all_dashboard_users, orphaned_dashboard_users, desired_products_by_email)

    @staticmethod
    def normalize_email(email):
        '''
        :type email: str
        '''
        return email.strip().lower();
        
class DashboardConnectors(object):
    def __init__(self, main_connector, trusted_connectors):
        '''
        :type main_connector: aedash.sync.connector.dashboard.DashboardConnector
        :type trusted_connectors: dict(str, aedash.sync.connector.dashboard.DashboardConnector)
        '''
        self.main_connector = main_connector
        self.trusted_connectors = trusted_connectors
        
        connectors = {
            MAIN_ORGANIZATION_NAME: main_connector
        }
        connectors.update(trusted_connectors)
        self.connectors = connectors
        
    def get_main_connector(self):
        return self.main_connector
    
    def get_trusted_connectors(self):
        return self.trusted_connectors
     
    def execute_actions(self):
        while True:
            had_work = False
            for connector in self.connectors.itervalues():
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
        
if True and __name__ == '__main__':
    mappings = {
        'acrobat': [Product("Default Acrobat Pro DC configuration", 'trusted')]
    }

    import connector.directory
    import connector.directory_csv
    csv_options = {
        'file_path': "data/test.csv",
    }    
    directory_connector = connector.directory.DirectoryConnector(connector.directory_csv)
    directory_connector.initialize(csv_options)

    dashboard_main_options = {
        'enterprise': {
            'org_id': "210DB41957FFDC210A495E53@AdobeOrg",
            'api_key': "4839484fa90147d6bb88f8db0c791ff1",
            'client_secret': "f907d26e-416e-4bbb-9c3e-7aa2dc439208",
            'tech_acct': "0E3B6A995806C4BE0A495CC7@techacct.adobe.com",
            'priv_key_path': "data/1/private1.key"
        }
    }
    dashboard_trusted_options = {
        'enterprise': {
            'org_id': "AD0F754C57FFF69A0A495E58@AdobeOrg",
            'api_key': "55561e5ccfd048c0b136dbec5f9904e8",
            'client_secret': "cf8cb4e6-89bf-4f2b-9b24-f048a7fee153",
            'tech_acct': "0ABD91645806C7500A495E57@techacct.adobe.com",
            'priv_key_path': "data/2/private2.key"
        }
    }
    import connector.dashboard
    dashboard_main_connector = connector.dashboard.DashboardConnector(dashboard_main_options)
    dashboard_trusted_connector = connector.dashboard.DashboardConnector(dashboard_trusted_options)

    dashboard_connectors = DashboardConnectors(dashboard_main_connector, {'trusted': dashboard_trusted_connector})

    rule_processor = RuleProcessor({})
    rule_processor.read_desired_user_products(mappings, directory_connector)
    rule_processor.process_dashboard_users(dashboard_connectors)
    
#    dashboard_connectors.execute_actions()
    
    a = 0
    a += 1
