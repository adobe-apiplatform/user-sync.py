import email.utils
import helper
import json
import logging
import math
import random
import time
from umapi import UMAPI, Action
from umapi.auth import Auth, JWT, AccessRequest
from umapi.error import UMAPIError, UMAPIRetryError, UMAPIRequestError
from umapi.helper import iter_paginate

import jwt
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

try:
    jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))
except:
    pass

class DashboardConnector(object):
    name = 'connector.aedash'
    
    def __init__(self, caller_options):
        '''
        :type caller_options: dict
        '''
        options = {
            'server': {
                'host': 'usermanagement.adobe.io',
                'endpoint': '/v2/usermanagement',
                'ims_host': 'ims-na1.adobelogin.com',
                'ims_endpoint_jwt': '/ims/exchange/jwt'
            },
            'logger_name': DashboardConnector.name,
            'test_mode': False,
        }
        if ('server' in caller_options):
            caller_server_options = caller_options['server']
            caller_server_options.pop('server', None)
            if (isinstance(caller_server_options, dict)):
                options['server'].update(caller_server_options)
        options.update(caller_options)
        
        required_options = [
            'enterprise.org_id',
            'enterprise.api_key',
            'enterprise.client_secret',
            'enterprise.tech_acct',
            'enterprise.priv_key_path'
        ]

        validation_result, validation_issue = helper.validate_options(options, required_options)
        if not validation_result:
            raise Exception('%s for connector: %s' % (validation_issue, DashboardConnector.name))

        self.options = options;        
        self.logger = logger = helper.create_logger(options)
        
        server_options = options['server']
        enterprise_options = options['enterprise']
                
        ims_host = server_options['ims_host']
        self.org_id = org_id = enterprise_options['org_id']
        api_key = enterprise_options['api_key']
        private_key_file_path = enterprise_options['priv_key_path']
        ims_url = "https://" + ims_host + server_options['ims_endpoint_jwt']
        um_endpoint = "https://" + server_options['host'] + server_options['endpoint']    
        
        # the JWT object build the JSON Web Token
        logger.info('Creating jwt for org id: "%s" using private key file: "%s"', org_id, private_key_file_path)            
        with open(private_key_file_path, 'r') as private_key_file:
            adobe_jwt_request = JWT(
                org_id,
                enterprise_options['tech_acct'],
                ims_host,
                api_key,
                private_key_file
            )
        adobe_jwt = adobe_jwt_request();
        logger.info('Created jwt with length: %d', len(adobe_jwt))            

        # when called, the AccessRequest object retrieves an access token from IMS
        logger.info('Requesting access from: "%s" for api_key: "%s"', ims_url, api_key)            
        access_request = AccessRequest(
            ims_url,
            api_key,
            enterprise_options['client_secret'],
            adobe_jwt
        )        
        access_token = access_request()
        logger.info('Received access token with length: %d', len(access_token))            
    
        # initialize Auth object for API requests
        auth = Auth(api_key, access_token)
        self.api_delegate = api_delegate = ApiDelegate(UMAPI(um_endpoint, auth, options['test_mode']), logger)
        logger.info('API initialized on: %s', um_endpoint)
        
        self.action_manager = ActionManager(api_delegate, org_id, logger)
        
    def get_users(self):
        return list(self.iter_users())

    def iter_users(self):
        users = {}
        for u in iter_paginate(self.api_delegate.users, self.org_id):
            email = u['email'] 
            if not (email in users):
                users[email] = u            
                yield u
    
    def get_action_manager(self):
        return self.action_manager
    
    def send_commands(self, commands, callback = None):
        '''
        :type commands: Commands
        :type callback: callable(umapi.Action, bool, dict)
        '''
        if (len(commands) > 0):
            username = commands.username
            domain = commands.domain
            action_options = {
                'user': username
            }
            if (domain != None):
                action_options['domain'] = domain        
            action = Action(**action_options)
            for command in commands.do_list:
                action.do(**{command[0]: command[1]})
                
            test_mode = self.options.get('test_mode')
            action_log_level = logging.INFO if test_mode else logging.DEBUG
            self.logger.log(action_log_level, 'Adding request:\n%s', json.dumps(action.data))
            self.get_action_manager().add_action(action, callback)

class Commands(object):
    def __init__(self, username, domain):
        '''
        :type username: str
        :type domain: str
        '''
        self.username = username
        self.domain = domain
        self.do_list = []

    def add_products(self, products_to_add):
        '''
        :type products_to_add: set(str)
        '''
        if (products_to_add != None and len(products_to_add) > 0):
            products = Commands.get_json_serializable(products_to_add)
            self.do_list.append(('add', products))

    def remove_products(self, products_to_remove):
        '''
        :type products_to_remove: set(str)
        '''
        if (products_to_remove != None and len(products_to_remove) > 0):
            products = Commands.get_json_serializable(products_to_remove)
            self.do_list.append(('remove', products))
    
    def add_federated_user(self, attributes):
        '''
        :type attributes: dict
        '''
        self.do_list.append(('createFederatedID', attributes))

    def add_enterprise_user(self, attributes):
        '''
        :type attributes: dict
        '''
        self.do_list.append(('createEnterpriseID', attributes))

    def __len__(self):
        return len(self.do_list)
            
    @staticmethod
    def get_json_serializable(value):
        result = value
        if isinstance(value, set):
            result = list(value)
        return result
    
    
class ActionManager(object):
    max_actions = 10

    def __init__(self, api_delegate, org_id, logger):
        '''
        :type api_delegate: ApiDelegate
        :type org_id: str
        :type logger: logging.Logger
        '''
        self.items = []
        self.api_delegate = api_delegate
        self.org_id = org_id
        self.logger = logger.getChild('action')
        self.next_request_id = 1;

    def add_action(self, action, callback = None):
        '''
        :type action: umapi.Action
        :type callback: callable(umapi.Action, bool, dict)
        '''
        action.data['requestID'] = request_id = 'action_%d' % self.next_request_id
        self.next_request_id += 1
        
        item = {
            'request_id': request_id,
            'action': action,
            'callback': callback
        }
        self.items.append(item)
        if len(self.items) >= self.max_actions:
            self.execute()
    
    def has_work(self):
        return len(self.items) > 0        

    def execute(self):
        num_attempts = 0
        num_attempts_max = 4

        items = self.items
        self.items = []

        while True:
            num_attempts += 1

            if num_attempts > num_attempts_max:
                self.logger.warn("FAILURE NO MORE RETRIES, SKIPPING...")
                break

            is_request_error = False
            try:
                res = self.api_delegate.action(self.org_id, [item['action'] for item in items])
            except UMAPIRequestError as e:
                is_request_error = True
                res = e.result
            except UMAPIRetryError as e:
                num_attempts = num_attempts_max
                continue
            except UMAPIError as e:
                self.logger.warn("ERROR -- %s - %s", e.res.status_code, e.res.text)
                break

            error_by_request_id = None
            if (res != None):
                log_level = logging.DEBUG if res['result'] == 'success' else logging.WARN 
                self.logger.log(log_level, 'Result %s -- %d completed, %d failed', res['result'], res['completed'], res['notCompleted'])

                if ('errors' in res):
                    error_by_request_id = {}
                    for error in res['errors']:
                        if ('message' in error or 'errorCode' in error):
                            self.logger.info('Error code: "%s" message: "%s"', error.get('errorCode'), error.get('message'))
                        if ('requestID' in error):
                            request_id = error['requestID']
                            error_by_request_id[request_id] = error
            elif is_request_error:
                self.logger.warn("Unknown result")

            
            for item in items:
                item_callback = item['callback']
                item_error = error_by_request_id.get(item['request_id']) if  error_by_request_id != None else None
                item_is_success = (not is_request_error) and item_error == None 
                if (callable(item_callback)):
                    item_callback(item['action'], item_is_success, item_error)
            break
        
class ApiDelegate(object):
    num_attempts_max = 4
    backoff_exponential_factor = 15  # seconds
    backoff_random_delay_max = 5  # seconds

    def __init__(self, api, logger):
        '''
        :type api: umapi.Api
        :type logger: logging.Logger
        '''
        self.api = api
        self.logger = logger.getChild('api')
    
    def users(self, *args):
        return self.make_api_call(self.api.users, args)
    
    def action(self, *args): 
        return self.make_api_call(self.api.action, args)
    
    def make_api_call(self, api_call, args):
        '''
        :type api_call: callable
        :type args: list
        '''
        num_attempts = 0
        while True:
            num_attempts += 1
            try:
                res = api_call(*args)
                break
            except UMAPIRetryError as e:
                self.logger.info("Retry error: %s", e.res.status_code)
                if num_attempts >= self.num_attempts_max:
                    self.logger.info("Retry max attempts reached")
                    raise e
                
                if "Retry-After" in e.res.headers:
                    retry_after_date = email.utils.parsedate_tz(e.res.headers["Retry-After"])
                    if retry_after_date is not None:
                        # header contains date
                        time_backoff = int(email.utils.mktime_tz(retry_after_date) - time.time())
                    else:
                        # header contains delta seconds
                        time_backoff = int(e.res.headers["Retry-After"])
                else:
                    # use exponential backoff with random delay
                    time_backoff = int(math.pow(2, num_attempts - 1)) * \
                                   self.backoff_exponential_factor + \
                                   random.randint(0, self.backoff_random_delay_max)
    
                self.logger.info("Retrying in %d seconds...", time_backoff)
                time.sleep(time_backoff)

        return res
        
    
if True and __name__ == '__main__':
    o1 = object()
    o2 = object()
    d = {}
    d[o1] = o1
    d[o2] = o2
    
    l = set()
    s = set()
    l1 = list()
    
    s1 = l - s
    
    options1 = {
        'enterprise': {
            'org_id': "7EF5AE375630F4CD7F000101@AdobeOrg",
            'api_key': "e604c71a2f624567b76528b5b9191f75",
            'client_secret': "56a9b8f4-b068-4319-a86a-4c71e9af7362",
            'tech_acct': "88C42DEA571F99AB7F000101@techacct.adobe.com",
            'priv_key_path': "adobe.io.private.der"
        }
    }
    options2 = {
        'enterprise': {
            'org_id': "210DB41957FFDC210A495E53@AdobeOrg",
            'api_key': "4839484fa90147d6bb88f8db0c791ff1",
            'client_secret': "f907d26e-416e-4bbb-9c3e-7aa2dc439208",
            'tech_acct': "0E3B6A995806C4BE0A495CC7@techacct.adobe.com",
            'priv_key_path': "data/1/private1.key"
        }
    }
    
    options3 = {
        'enterprise': {
            'org_id': "AD0F754C57FFF69A0A495E58@AdobeOrg",
            'api_key': "55561e5ccfd048c0b136dbec5f9904e8",
            'client_secret': "cf8cb4e6-89bf-4f2b-9b24-f048a7fee153",
            'tech_acct': "0ABD91645806C7500A495E57@techacct.adobe.com",
            'priv_key_path': "data/2/private2.key"
        }
    }
    
    options = options3
    
    import requests
    
    connector = DashboardConnector(options)
    #api = connector.api
#    res = api._call('/organizations/%s/users/%s' % (connector.org_id, 'davidy@ensemble.ca'), requests.get)
#    res = api._call('/%s/user-groups' % connector.org_id, requests.get)
    #res = api._call('/%s/products' % connector.org_id, requests.get)
    #res = api._call('/groups/%s/0' % connector.org_id, requests.get)
    #res = api._call('/users/%s/0?domain=%s' % (connector.org_id, 'ensemble.ca'), requests.get)

#    for i in range(1, 100):
    users = connector.get_users()

    
    for u in users:
        if ("groups" in u):
            print(u)
            
    action2 = Action(user='davidy@ensemble.ca').do(
            add=['Default Acrobat Pro DC configuration'],
        )
         
    action3 = Action(user='davidy@ensemble.ca').do(
            remove=['Default Acrobat Pro DC configuration'],
        )
    
    action1 = Action(user='davidy@ensemble.ca').do(
            update={
        "firstname" : "David5"
       }
    )
    action = Action(user='davidy@ensemble.ca').do(
            removeFromOrg=
                { 
                  "removedDomain" : "ensemble.ca"
                }
       
    )
    manager = connector.get_action_manager()
    
    for i in range(1, 100):
        manager.add_action(action2)
        manager.execute()
    
    a=0
    a+=1
    
    '''
    Default Acrobat Pro DC configuration
    '''
