import helper
from umapi import UMAPI
from umapi.auth import Auth, JWT, AccessRequest
from umapi.helper import paginate

import jwt
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

class AdobeConnector(object):
    name = 'connector.adobe'
    
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
            'logger_name': AdobeConnector.name,
            'test_mode': False
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
            raise Exception('%s for connector: %s' % (validation_issue, AdobeConnector.name))

        self.options = options;        
        self.logger = logger = helper.create_logger(options)
        
        server_options = options['server']
        enterprise_options = options['enterprise']
        
        jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))

        ims_host = server_options['ims_host']
        org_id = enterprise_options['org_id']
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
        self.api = UMAPI(um_endpoint, auth, options['test_mode'])
        logger.info('API initialized on: %s', um_endpoint)
        
    def get_users(self):
        users = {}
        options = self.options
        for u in paginate(self.api.users, options['enterprise']['org_id']):
            email = u['email'] 
            users[email] = u
        return users.values()


if True and __name__ == '__main__':
    options = {
        'enterprise': {
            'org_id': "7EF5AE375630F4CD7F000101@AdobeOrg",
            'api_key': "e604c71a2f624567b76528b5b9191f75",
            'client_secret': "56a9b8f4-b068-4319-a86a-4c71e9af7362",
            'tech_acct': "88C42DEA571F99AB7F000101@techacct.adobe.com",
            'priv_key_path': "adobe.io.private.der"
        }
    }
    options = {
        'enterprise': {
            'org_id': "210DB41957FFDC210A495E53@AdobeOrg",
            'api_key': "4839484fa90147d6bb88f8db0c791ff1",
            'client_secret': "f907d26e-416e-4bbb-9c3e-7aa2dc439208",
            'tech_acct': "0E3B6A995806C4BE0A495CC7@techacct.adobe.com",
            'priv_key_path': "1/private.key"
        }
    }
    
    options = {
        'enterprise': {
            'org_id': "AD0F754C57FFF69A0A495E58@AdobeOrg",
            'api_key': "55561e5ccfd048c0b136dbec5f9904e8",
            'client_secret': "cf8cb4e6-89bf-4f2b-9b24-f048a7fee153",
            'tech_acct': "0ABD91645806C7500A495E57@techacct.adobe.com",
            'priv_key_path': "2/private.key"
        }
    }
    
    connector = AdobeConnector(options)
    users = connector.get_users()
    for u in users:
        if ("groups" in u):
            print(u)
    a=0
    a+=1
