import time
import jwt
import requests
import json
import yaml
from urllib.parse import urlencode

class UMAPIConfig:

    def __init__(self, logs):

        self.logs = logs

        umapi_yaml_config = yaml.load(open('connector-umapi.yml'))

        # read server parameters
        self.host = umapi_yaml_config['server']['host']
        self.ims_host = umapi_yaml_config['server']['ims_host']
        self.endpoint = umapi_yaml_config['server']['endpoint']
        self.ims_endpoint_jwt = umapi_yaml_config['server']['ims_endpoint_jwt']

        # read enterprise parameters
        self.org_id = umapi_yaml_config['enterprise']['org_id']
        self.tech_acct = umapi_yaml_config['enterprise']['tech_acct']
        self.api_key = umapi_yaml_config['enterprise']['api_key']
        self.client_secret = umapi_yaml_config['enterprise']['client_secret']
        self.priv_key_filename = umapi_yaml_config['enterprise']['priv_key_path']

        self.jwt_token = ""
        self.access_token = ""

        self.create_json_token()


    def create_json_token(self):
        """
        This function creates a json token for UMAPI integration.
        :return:
        """

        # Set the expiration time for the JSON Web Token to one day from the current time. This is a typical and
        # recommended validity period.
        expiry_time = int(time.time()) + 60*60*24

        # create payload
        payload = {
            'exp': expiry_time,
            'iss': self.org_id,
            'sub': self.tech_acct,
            'aud': "https://" + self.ims_host + "/c/" + self.api_key
        }

        # define scopes
        scopes = ["ent_user_sdk"]

        # add scopes to the payload
        for scope in scopes:
            payload["https://" + self.ims_host + "/s/" + scope] = True

        # Read the private key we will use to sign the JWT.
        priv_key_file = open(self.priv_key_filename)
        priv_key = priv_key_file.read()
        priv_key_file.close()

        # create JSON Web Token, signing it with the private key.
        self.jwt_token = jwt.encode(payload, priv_key, algorithm='RS256')

        # decode bytes into string
        self.jwt_token = self.jwt_token.decode("utf-8")

    def get_access_token(self):
        """
        This function will get an access token for UMAPI integration.
        :return:
        """

        # REQUEST ACCESS TOKEN
        self.logs['process'].info("Requesting access token...")

        # method parameters. The credentials are placed in the body of the POST request. Notice that the "client_id"
        # value is your API key.
        url = "https://" + self.ims_host + self.ims_endpoint_jwt + '/'

        headers = {
            "Content-Type" : "application/x-www-form-urlencoded",
            "Cache-Control" : "no-cache"
        }
        body_credentials = {
            "client_id": self.api_key,
            "client_secret": self.client_secret,
            "jwt_token": self.jwt_token
        }
        body = urlencode(body_credentials)

        # send http request
        res = requests.post(url, headers=headers, data=body)
        # self.logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        # evaluate response
        if res.status_code == 200:

            self.logs['process'].info('Access Token Granted...')

            # extract token
            self.access_token = json.loads(res.text)['access_token']

            return self.access_token

        else:
            # print response
            self.logs['error'].error(res.status_code)
            self.logs['error'].error(res.headers)
            self.logs['error'].error(res.text)
            exit(res.status_code)

    def get_action_url(self):
        """
        This function returns an action url for API calls.
        :return: str
        """

        return "https://" + self.host + self.endpoint + "/action/" + self.org_id

    def get_custom_url(self, action):
        """
        This function will allow the user to get a custom url for API calls
        :param action: str
        :return: str
        """

        return "https://" + self.host + self.endpoint + "/" + action + "/" + self.org_id

    def get_header(self):
        """
        This function returns the header for UMAPI API calls.
        :return: dict()
        """

        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "x-api-key": self.api_key,
            "Authorization": "Bearer " + self.access_token}

        return headers

    def get_umapi_config_dict(self):
        """
        This function will return the configuration needed to make API calls to UMAPI
        :return: dict()
        """

        temp_dict = dict()
        temp_dict['access_token'] = self.get_access_token()
        temp_dict['header'] = self.get_header()
        temp_dict['url'] = self.get_action_url()

        return temp_dict