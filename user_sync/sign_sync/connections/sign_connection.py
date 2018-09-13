import requests
import user_sync.config
import codecs

from user_sync.error import AssertionException

class SIGNConfig:

    def __init__(self, logs):

        self.logs = logs
        self.sign_config = self.load_sign_config()

        self.sign_config.yml = self.sign_config.value

        # read server parameters
        self.host = self.sign_config.yml['server']['host']
        self.endpoint = self.sign_config.yml['server']['endpoint_v5']

        # read condition parameters
        self.version = self.sign_config.yml['conditions']['version']
        self.connector = self.sign_config.yml['conditions']['connector']


        # read enterprise parameters
        self.integration = self.sign_config.yml['enterprise']['integration']
        self.email = self.sign_config.yml['enterprise']['email']

        if self.connector == 'umapi':
            self.account_admin = self.sign_config.yml['umapi_conditions']['account_admin_groups']
            self.ignore_admin_group = self.sign_config.yml['umapi_conditions']['ignore_admin_groups']
            self.product_group = self.sign_config.yml['umapi_conditions']['product_group']
            self.ignore_group = self.sign_config.yml['umapi_conditions']['ignore_groups']
        else:
            self.account_admin = None
            self.ignore_admin_group = None

    def load_sign_config(self):


        config_filename = 'sign_sync/connector-sign-sync.yml'
        config_encoding = 'utf-8'
        try:
            codecs.lookup(config_encoding)
        except LookupError:
            raise AssertionException("Unknown encoding '%s' specified for configuration files" % config_encoding)
        user_sync.config.ConfigFileLoader.config_encoding = config_encoding
        main_config_content = user_sync.config.ConfigFileLoader.load_root_config(config_filename)
        return user_sync.config.DictConfig("<%s>" % config_filename, main_config_content)


    def get_sign_url(self, ver=None):
        """
        This function returns the SIGN url.
        :param ver: str
        :return: str
        """

        if ver is None:
            return "https://" + self.host + self.endpoint + "/"
        else:
            return "https://" + self.host + "/" + ver + "/"

    def get_sign_header(self, ver=None):
        """
        This function returns the SIGN header
        :param ver: str
        :return: dict()
        """

        if self.version == 'v5' or ver == 'v5':
            headers = {
                "Access-Token": self.integration
            }
        else:
            headers = {
                "Authorization": "Bearer {}".format(self.integration)
            }

        return headers


    def get_priv_settings(self):
        """
        This function returns a list of admin privileges from sign.config (account_admin_groups)
        :return: list[]
        """
        self.logs.info('Setting Account Admin Settings...')

        return self.account_admin

    def get_ignore_priv_settings(self):
        """
        This function return a list of all ignore admin groups from sign.config (ignore_admin_groups)
        :return:
        """

        self.logs.info('Setting Ignore Admin Groups Settings...')

        return self.ignore_admin_group

    def get_ignore_groups_setting(self):
        """
        This function returns a list of all ignore groups from sign.config (ignore_group)
        :return:
        """

        self.logs.info("Setting Ignore Groups Settings...")

        return self.ignore_group

    def get_product_groups_settings(self):

        self.logs.info("Setting Product Group Settings...")

        return self.product_group

    def validate_integration_key(self, headers, url):
        """
        This function validates that the SIGN integration key is valid.
        :param headers: dict()
        :param url: str
        :return:
        """

        self.logs.info("Validating Integration Key...")

        if self.version == "v5":
            res = requests.get(url + "base_uris", headers=headers)
        else:
            res = requests.get(url + "baseUris", headers=headers)

        # self.logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        if res.status_code == 200:

            self.logs.info('Integration Key Validated...')

        else:
            # print response
            self.logs.error(res.status_code)
            self.logs.error(res.headers)
            self.logs.error(res.text)
            exit(res.status_code)

    def get_config_dict(self):
        """
        This function will grab all the data from the configuration file and create a dict of information
        :return: dict()
        """

        sign_config = dict()
        sign_config['condition'] = dict()
        sign_config['url'] = self.get_sign_url()
        sign_config['header'] = self.get_sign_header()
        sign_config['group'] = self.get_sign_group(sign_config['header'], sign_config['url'], self.logs)
        sign_config['email'] = self.email
        sign_config['connector'] = self.connector
        sign_config['condition']['ignore_groups'] = self.get_ignore_groups_setting()

        if self.connector == 'umapi':
            sign_config['condition']['account_admin_groups'] = self.get_priv_settings()
            sign_config['condition']['ignore_admin_groups'] = self.get_ignore_priv_settings()
            sign_config['condition']['product_group'] = self.get_product_groups_settings()

        return sign_config

    @staticmethod
    def get_sign_group(header, url, logs):
        """
        This function creates a list of groups that's in Adobe Sign Groups.
        :param header: str
        :param url: str
        :param logs: dict()
        :return: list[]
        """

        res = requests.get(url + 'groups', headers=header)
        # logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        sign_groups = res.json()

        temp_list = {}

        for group in sign_groups['groupInfoList']:
            temp_list[group['groupName']] = group['groupId']

        return temp_list

    @staticmethod
    def get_user_data(header, url, user_id, logs):

        res = requests.get(url + 'users/' + user_id, headers=header)
        data = res.json()

        #API LOG
        logs.info("{} {} {}".format(res.request, res.status_code, res.url))

        return data
