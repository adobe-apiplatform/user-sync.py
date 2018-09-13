class UMAPIConfig:

    def __init__(self, config_loader, connector, logs):

        self.logs = logs
        self.umapi_config = config_loader.get_umapi_options()[0]

        # read server parameters
        self.host = self.umapi_config['server']['host']
        self.ims_host = self.umapi_config['server']['ims_host']
        self.endpoint = self.umapi_config['server']['endpoint']
        self.ims_endpoint_jwt = self.umapi_config['server']['ims_endpoint_jwt']

        # read enterprise parameters
        self.org_id = self.umapi_config['enterprise']['org_id']
        self.tech_acct = self.umapi_config['enterprise']['tech_acct']
        self.api_key = self.umapi_config['enterprise']['api_key']
        self.client_secret = self.umapi_config['enterprise']['client_secret']
        self.priv_key_filename = self.umapi_config['enterprise']['priv_key_path']

        primary_umapi_config, secondary_umapi_configs = config_loader.get_umapi_options()
        primary_name = '.primary' if secondary_umapi_configs else ''
        umapi_primary_connector = connector.UmapiConnector(primary_name, primary_umapi_config)
        self.access_token = umapi_primary_connector.connection.auth.access_token


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
        temp_dict['access_token'] = self.access_token
        temp_dict['header'] = self.get_header()
        temp_dict['url'] = self.get_action_url()

        return temp_dict