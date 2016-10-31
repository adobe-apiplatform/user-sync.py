from umapi import Action

ENTERPRISE_IDENTITY_TYPE = 'ENTERPRISE_ID'
FEDERATED_IDENTITY_TYPE = 'FEDERATED_ID'

MAIN_ORGANIZATION_NAME = None

class RuleProcessor(object):
    
    def __init__(self, options):
        self.options = options        
        self.customer_user_by_email = {}
        self.desired_products_by_organization = {}
        self.orphaned_adobe_users_by_organization = {}
    
    def read_desired_user_products(self, mappings, customer_connector):
        '''
        :type mappings: dict(str, list(AdobeProduct)
        :type customer_connector: connector.customer.CustomerConnector
        '''
        customer_user_by_email = self.customer_user_by_email
        desired_products_by_organization = self.desired_products_by_organization
        
        customer_groups = mappings.keys()
        for customer_user in customer_connector.iter_users_with_groups(customer_groups):
            email = RuleProcessor.normalize_email(customer_user['email'])
            customer_user_by_email[email] = customer_user             
            for group in customer_user['groups']:
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
                    customer_user = self.customer_user_by_email[email]
                    self.add_products_for_connector(customer_user, desired_products, adobe_connector)
                else:
                    self.add_adobe_user(email, adobe_connectors)
                    added_adobe_emails.add(email)
            
    def add_adobe_user(self, email, adobe_connectors):
        '''
        :type email: str
        :type adobe_connectors: AdobeConnectors
        '''
        customer_user = self.customer_user_by_email[email]

        attributes = {}
        attributes['email'] = email
        attributes['firstname'] = customer_user['firstname']
        attributes['lastname'] = customer_user['lastname']
        attributes['country'] = customer_user['country']
        
        action_builder = ActionBuilder()
        action_builder.add_user(ENTERPRISE_IDENTITY_TYPE, attributes)
        desired_products_by_email = self.desired_products_by_organization.get(MAIN_ORGANIZATION_NAME)
        if (desired_products_by_email != None):
            desired_products = desired_products_by_email.get(email)
            action_builder.add_products(desired_products)
        action = action_builder.create_action(customer_user['username'], customer_user['domain'])

        def callback(create_action, is_success, error):
            if is_success:
                self.add_products_for_trusted_connectors(customer_user, adobe_connectors.trusted_connectors)
        adobe_connectors.get_main_connector().get_action_manager().add_action(action, callback)

    def add_products_for_trusted_connectors(self, customer_user, trusted_adobe_connectors):
        '''
        :type customer_user: dict
        :type trusted_adobe_connectors: dict(str, connector.adobe.AdobeConnector)
        '''
        desired_products_by_organization = self.desired_products_by_organization    
        for organization_name, adobe_connector in trusted_adobe_connectors.iteritems():
            desired_products_by_email = desired_products_by_organization.get(organization_name)
            if desired_products_by_email != None:
                desired_products = desired_products_by_email.get(customer_user['email'])
                self.add_products_for_connector(customer_user, desired_products, adobe_connector)

    def add_products_for_connector(self, customer_user, desired_products, adobe_connector):
        '''
        :type customer_user: dict
        :type desired_products: set(str)
        :type trusted_adobe_connectors: dict(str, connector.adobe.AdobeConnector)
        '''
        action_builder = ActionBuilder()
        action_builder.add_products(desired_products)
        if action_builder.has_commands():
            action = action_builder.create_action(customer_user['username'], customer_user['domain'])
            adobe_connector.get_action_manager().add_action(action)
            
    def update_adobe_users_for_connector(self, organization_name, adobe_connector):
        '''
        :type organization_name: str
        :type adobe_connector: connector.adobe.AdobeConnector
        '''
        customer_user_by_email = self.customer_user_by_email
        
        desired_products_by_email = self.desired_products_by_organization.get(organization_name)
        desired_products_by_email = {} if desired_products_by_email == None else desired_products_by_email.copy()        
        all_adobe_users = {}
        orphaned_adobe_users = {}
        
        for adobe_user in adobe_connector.iter_users():
            email = RuleProcessor.normalize_email(adobe_user['email'])
            all_adobe_users[email] = adobe_user
            
            customer_user = customer_user_by_email.get(email)
            if (customer_user == None):
                orphaned_adobe_users[email] = adobe_user
                continue                    
                
            desired_products = desired_products_by_email.pop(email, None)
            if desired_products == None:
                desired_products = set()
            current_products = adobe_user.get('groups')
            current_products = set() if current_products == None else set(current_products)
            
            products_to_add = desired_products - current_products
            products_to_remove = current_products - desired_products

            action_builder = ActionBuilder()
            action_builder.add_products(products_to_add)
            action_builder.remove_products(products_to_remove)
            if action_builder.has_commands():
                action = action_builder.create_action(customer_user['username'], customer_user['domain'])
                adobe_connector.get_action_manager().add_action(action)
                
        return (all_adobe_users, orphaned_adobe_users, desired_products_by_email)

    @staticmethod
    def normalize_email(email):
        '''
        :type email: str
        '''
        return email.strip().lower();

class ActionBuilder(object):
    def __init__(self):
        self.commands = []

    def add_products(self, products_to_add):
        '''
        :type products_to_add: set(str)
        '''
        if (products_to_add != None and len(products_to_add) > 0):
            products = ActionBuilder.get_json_serializable(products_to_add)
            self.commands.append(('add', products))

    def remove_products(self, products_to_remove):
        '''
        :type products_to_remove: set(str)
        '''
        if (products_to_remove != None and len(products_to_remove) > 0):
            products = ActionBuilder.get_json_serializable(products_to_remove)
            self.commands.append(('remove', products))
    
    def add_user(self, identity_type, attributes):
        '''
        :type identity_type: str
        :type attributes: dict
        '''
        action_name = 'createFederatedID' if identity_type == FEDERATED_IDENTITY_TYPE else 'createEnterpriseID' 
        self.commands.append((action_name, attributes))

    def has_commands(self):
        return len(self.commands) > 0
            
    def create_action(self, username, domain):
        '''
        :type username: str
        :type domain: str
        '''
        action_options = {
            'user': username
        }
        if (domain != None):
            action_options['domain'] = domain        
        action = Action(**action_options)
        for command in self.commands:
            action.do(**{command[0]: command[1]})
        return action    

    @staticmethod
    def get_json_serializable(value):
        result = value
        if isinstance(value, set):
            result = list(value)
        return result
        
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
        
if True and __name__ == '__main__':
    mappings = {
        'acrobat': [Product("Default Acrobat Pro DC configuration", 'trusted')]
    }

    import connector.customer
    import connector.customer_csv
    csv_options = {
        'filename': "test.csv",
    }    
    customer_connector = connector.customer.CustomerConnector(connector.customer_csv, csv_options)

    import connector.adobe
    adobe_main_options = {
        'enterprise': {
            'org_id': "210DB41957FFDC210A495E53@AdobeOrg",
            'api_key': "4839484fa90147d6bb88f8db0c791ff1",
            'client_secret': "f907d26e-416e-4bbb-9c3e-7aa2dc439208",
            'tech_acct': "0E3B6A995806C4BE0A495CC7@techacct.adobe.com",
            'priv_key_path': "connector/1/private.key"
        }
    }
    adobe_trusted_options = {
        'enterprise': {
            'org_id': "AD0F754C57FFF69A0A495E58@AdobeOrg",
            'api_key': "55561e5ccfd048c0b136dbec5f9904e8",
            'client_secret': "cf8cb4e6-89bf-4f2b-9b24-f048a7fee153",
            'tech_acct': "0ABD91645806C7500A495E57@techacct.adobe.com",
            'priv_key_path': "connector/2/private.key"
        }
    }
    adobe_main_connector = connector.adobe.AdobeConnector(adobe_main_options)
    adobe_trusted_connector = connector.adobe.AdobeConnector(adobe_trusted_options)

    adobe_connectors = AdobeConnectors(adobe_main_connector, {'trusted': adobe_trusted_connector})

    rule_processor = RuleProcessor({})
    rule_processor.read_desired_user_products(mappings, customer_connector)
    rule_processor.process_adobe_users(adobe_connectors)
    
    adobe_connectors.execute_actions()
    
    a = 0
    a+=1