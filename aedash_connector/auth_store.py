import os
import json
import datetime as dt
from umapi.auth import JWT, AccessRequest


def init(config, store_path):
    """
    Helper function to initialize AuthStore object from config

    :param config: Application config object
    :param store_path: Store file path
    :return: AuthStore object
    """

    # the JWT object build the JSON Web Token
    jwt = JWT(
        config['enterprise']['org_id'],
        config['enterprise']['tech_acct'],
        config['server']['ims_host'],
        config['enterprise']['api_key'],
        open(config['enterprise']['priv_key_path'], 'r')
    )

    # when called, the AccessRequest object retrieves an access token from IMS
    access_req = AccessRequest(
        "https://" + config['server']['ims_host'] + config['server']['ims_endpoint_jwt'],
        config['enterprise']['api_key'],
        config['enterprise']['client_secret'],
        jwt()
    )

    return AuthStore(store_path, access_req)


class AuthStore(object):
    ini_json = '{"token": "", "expiry": ""}'

    def __init__(self, store_path, access_req):
        self.store_path = store_path
        self.access_req = access_req

        # if auth store file does not exist, then initialize with skeleton JSON object
        if not os.path.exists(store_path):
            with open(store_path, 'w') as fp:
                fp.write(self.ini_json)
                fp.close()

    def token(self):
        """
        Get auth token

        Returns token from store if not expired, and requests new one if token is expired

        :return: token string
        """
        with open(self.store_path, 'r') as store_file:
            try:
                data = json.load(store_file)
            except ValueError:
                raise ValueError("Cannot decode auth store object")
            if data['expiry']:
                expiry = dt.datetime.strptime(data['expiry'], '%Y-%m-%d %H:%M:%S')
            else:
                expiry = dt.datetime.now()

            if expiry <= dt.datetime.now():
                token = self.access_req()
                data['expiry'] = self.access_req.expiry.strftime('%Y-%m-%d %H:%M:%S')
                data['token'] = token
                with open(self.store_path, 'w') as fp:
                    json.dump(data, fp)
                return token
            else:
                return data['token']
