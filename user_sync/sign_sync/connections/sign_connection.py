import requests
import yaml

class SIGNConfig:

    def __init__(self, logs, path=None):

        self.logs = logs

        if path is None:
            yml_sign_sync_config = yaml.load(open('sign_sync/connector-sign-sync.yml'))
        else:
            yml_sign_sync_config = yaml.load(open('../connector-sign-sync.yml'))

        # read server parameters
        self.host = yml_sign_sync_config['server']['host']

        # read condition parameters
        self.version = yml_sign_sync_config['conditions']['version']
        self.connector = yml_sign_sync_config['conditions']['connector']

        if self.version == 'v5':
            self.endpoint = yml_sign_sync_config['server']['endpoint_v5']
        elif self.version == 'v6':
            self.endpoint = yml_sign_sync_config['server']['endpoint_v6']
        else:
            self.logs['error'].error("Incorrect Version, Please Check Sign.Config Version Parameter")
            exit(0)

        # read enterprise parameters
        self.integration = yml_sign_sync_config['enterprise']['integration']
        self.email = yml_sign_sync_config['enterprise']['email']

        if self.connector == 'umapi':
            self.account_admin = yml_sign_sync_config['umapi_conditions']['account_admin_groups']
            self.ignore_admin_group = yml_sign_sync_config['umapi_conditions']['ignore_admin_groups']
            self.product_group = yml_sign_sync_config['umapi_conditions']['product_group']
            self.multi_group = yml_sign_sync_config['umapi_conditions']['multi_group']
            self.ignore_group = yml_sign_sync_config['umapi_conditions']['ignore_groups']
        else:
            self.account_admin = None
            self.ignore_admin_group = None


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

    def get_multi_group_setting(self):
        """
        This function returns a flag for multi-group movements from sign.config (multi_group)
        :return: boolean
        """

        self.logs['process'].info('Setting Multi Group Settings...')

        if self.multi_group.lower() == 'yes' or self.multi_group.lower() == 'no':
            if self.multi_group.lower() == 'yes':
                return True
            else:
                return False
        else:
            self.logs['error'].error('Multi Group Configuration Is Incorrect...')
            exit(0)

    def get_priv_settings(self):
        """
        This function returns a list of admin privileges from sign.config (account_admin_groups)
        :return: list[]
        """
        self.logs['process'].info('Setting Account Admin Settings...')

        account_list = self.account_admin.split(', ')

        return account_list

    def get_ignore_priv_settings(self):
        """
        This function return a list of all ignore admin groups from sign.config (ignore_admin_groups)
        :return:
        """

        self.logs['process'].info('Setting Ignore Admin Groups Settings...')

        ignore_list = self.ignore_admin_group.split(', ')

        return ignore_list

    def get_ignore_groups_setting(self):
        """
        This function returns a list of all ignore groups from sign.config (ignore_group)
        :return:
        """

        self.logs['process'].info("Setting Ignore Groups Settings...")

        ignore_list = self.ignore_group.split(', ')

        return ignore_list

    def get_product_groups_settings(self):

        self.logs['process'].info("Setting Product Group Settings...")

        product_group = self.product_group.split(', ')

        return product_group

    def validate_integration_key(self, headers, url):
        """
        This function validates that the SIGN integration key is valid.
        :param headers: dict()
        :param url: str
        :return:
        """

        self.logs['process'].info("Validating Integration Key...")

        if self.version == "v5":
            res = requests.get(url + "base_uris", headers=headers)
        else:
            res = requests.get(url + "baseUris", headers=headers)

        # self.logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        if res.status_code == 200:

            self.logs['process'].info('Integration Key Validated...')

        else:
            # print response
            self.logs['error'].error(res.status_code)
            self.logs['error'].error(res.headers)
            self.logs['error'].error(res.text)
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
        sign_config['condition']['multi_group'] = self.get_multi_group_setting()
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

        logs['api'].info("{} {} {}".format(res.request, res.status_code, res.url))

        return data
