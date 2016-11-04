from connector.adobe import Commands

ENTERPRISE_IDENTITY_TYPE = 'enterpriseID'
FEDERATED_IDENTITY_TYPE = 'federatedID'

MAIN_ORGANIZATION_NAME = None

class RuleProcessor(object):
    
    def __init__(self, options):
        self.options = options        
        self.directory_user_by_email = {}
        self.desired_products_by_organization = {}
        self.orphaned_adobe_users_by_organization = {}
    
    def read_desired_user_products(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(AdobeProduct)
        :type directory_connector: aedash.sync.connector.directory.DirectoryConnector
        '''
        directory_user_by_email = self.directory_user_by_email
        desired_products_by_organization = self.desired_products_by_organization
        
        directory_groups = mappings.keys()
        for directory_user in directory_connector.iter_users_with_groups(directory_groups):
            email = RuleProcessor.normalize_email(directory_user['email'])
            directory_user_by_email[email] = directory_user             
            for group in directory_user['groups']:
                adobe_products = mappings.get(group)
                if (adobe_products != None):
                    for adobe_product in adobe_products:
                        organization_name = adobe_product.organization_name
                        organization_desired_products = desired_products_by_organization.get(organization_name)
                        if (organization_desired_products == None):
                            desired_products_by_organization[organization_name] = organization_desired_products = {}
                        user_desired_products = organization_desired_products.get(email)
                        if (user_desired_products == None):
                            organization_desired_products[email] = user_desired_products = set()
                        user_desired_products.add(adobe_product.product_name)
        
    def process_adobe_users(self, adobe_connectors):
        '''
        :type adobe_connectors: AdobeConnectors
        '''
        added_adobe_emails = set()

        main_adobe_users, main_orphaned_adobe_users, main_unprocessed_products_by_email = self.update_adobe_users_for_connector(MAIN_ORGANIZATION_NAME, adobe_connectors.get_main_connector())
        self.orphaned_adobe_users_by_organization[MAIN_ORGANIZATION_NAME] = main_orphaned_adobe_users 
        for email in main_unprocessed_products_by_email.iterkeys():
            self.add_adobe_user(email, adobe_connectors)
            added_adobe_emails.add(email)

        for organization_name, adobe_connector in adobe_connectors.get_trusted_connectors().iteritems():
            _trusted_adobe_users, trusted_orphaned_adobe_users, trusted_unprocessed_products_by_email = self.update_adobe_users_for_connector(organization_name, adobe_connector)
            self.orphaned_adobe_users_by_organization[organization_name] = trusted_orphaned_adobe_users 
            for email, desired_products in trusted_unprocessed_products_by_email.iteritems():
                if (email in added_adobe_emails):
                    continue
                if (email in main_adobe_users):
                    directory_user = self.directory_user_by_email[email]
                    self.add_products_for_connector(directory_user, desired_products, adobe_connector)
                else:
                    self.add_adobe_user(email, adobe_connectors)
                    added_adobe_emails.add(email)
            
    def add_adobe_user(self, email, adobe_connectors):
        '''
        :type email: str
        :type adobe_connectors: AdobeConnectors
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
                self.add_products_for_trusted_connectors(directory_user, adobe_connectors.trusted_connectors)
        adobe_connectors.get_main_connector().send_commands(commands, callback)

    def add_products_for_trusted_connectors(self, directory_user, trusted_adobe_connectors):
        '''
        :type directory_user: dict
        :type trusted_adobe_connectors: dict(str, connector.adobe.AdobeConnector)
        '''
        desired_products_by_organization = self.desired_products_by_organization    
        for organization_name, adobe_connector in trusted_adobe_connectors.iteritems():
            desired_products_by_email = desired_products_by_organization.get(organization_name)
            if desired_products_by_email != None:
                desired_products = desired_products_by_email.get(directory_user['email'])
                self.add_products_for_connector(directory_user, desired_products, adobe_connector)

    def add_products_for_connector(self, directory_user, desired_products, adobe_connector):
        '''
        :type directory_user: dict
        :type desired_products: set(str)
        :type trusted_adobe_connectors: dict(str, connector.adobe.AdobeConnector)
        '''
        commands = Commands(directory_user['username'], directory_user['domain'])
        commands.add_products(desired_products)
        adobe_connector.send_commands(commands)
            
    def update_adobe_users_for_connector(self, organization_name, adobe_connector):
        '''
        :type organization_name: str
        :type adobe_connector: connector.adobe.AdobeConnector
        '''
        directory_user_by_email = self.directory_user_by_email
        
        desired_products_by_email = self.desired_products_by_organization.get(organization_name)
        desired_products_by_email = {} if desired_products_by_email == None else desired_products_by_email.copy()        
        all_adobe_users = {}
        orphaned_adobe_users = {}
        
        for adobe_user in adobe_connector.iter_users():
            email = RuleProcessor.normalize_email(adobe_user['email'])
            all_adobe_users[email] = adobe_user
            
            directory_user = directory_user_by_email.get(email)
            if (directory_user == None):
                orphaned_adobe_users[email] = adobe_user
                continue                    
                
            desired_products = desired_products_by_email.pop(email, None)
            if desired_products == None:
                desired_products = set()
            current_products = adobe_user.get('groups')
            current_products = set() if current_products == None else set(current_products)
            
            products_to_add = desired_products - current_products
            products_to_remove = current_products - desired_products

            commands = Commands(directory_user['username'], directory_user['domain'])
            commands.add_products(products_to_add)
            commands.remove_products(products_to_remove)
            adobe_connector.send_commands(commands)
                
        return (all_adobe_users, orphaned_adobe_users, desired_products_by_email)

    @staticmethod
    def normalize_email(email):
        '''
        :type email: str
        '''
        return email.strip().lower();
        
class AdobeConnectors(object):
    def __init__(self, main_connector, trusted_connectors):
        '''
        :type main_connector: connector.adobe.AdobeConnector
        :type trusted_connectors: dict(str, connector.adobe.AdobeConnector)
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
    directory_connector = connector.directory.DirectoryConnector(connector.directory_csv, csv_options)

    import connector.adobe
    adobe_main_options = {
        'enterprise': {
            'org_id': "210DB41957FFDC210A495E53@AdobeOrg",
            'api_key': "4839484fa90147d6bb88f8db0c791ff1",
            'client_secret': "f907d26e-416e-4bbb-9c3e-7aa2dc439208",
            'tech_acct': "0E3B6A995806C4BE0A495CC7@techacct.adobe.com",
            'priv_key_path': "data/1/private1.key"
        }
    }
    adobe_trusted_options = {
        'enterprise': {
            'org_id': "AD0F754C57FFF69A0A495E58@AdobeOrg",
            'api_key': "55561e5ccfd048c0b136dbec5f9904e8",
            'client_secret': "cf8cb4e6-89bf-4f2b-9b24-f048a7fee153",
            'tech_acct': "0ABD91645806C7500A495E57@techacct.adobe.com",
            'priv_key_path': "data/2/private2.key"
        }
    }
    adobe_main_connector = connector.adobe.AdobeConnector(adobe_main_options)
    adobe_trusted_connector = connector.adobe.AdobeConnector(adobe_trusted_options)

    adobe_connectors = AdobeConnectors(adobe_main_connector, {'trusted': adobe_trusted_connector})

    rule_processor = RuleProcessor({})
    rule_processor.read_desired_user_products(mappings, directory_connector)
    rule_processor.process_adobe_users(adobe_connectors)
    
#    adobe_connectors.execute_actions()
    
    a = 0
    a+=1
