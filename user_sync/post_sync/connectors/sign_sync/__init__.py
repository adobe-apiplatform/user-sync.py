import logging
from user_sync.post_sync import PostSyncConnector
from user_sync.config import DictConfig, OptionsBuilder


class SignConnector(PostSyncConnector):
    name = 'sign_sync'

    def __init__(self, config_options):
        super().__init__()
        self.logger = logging.getLogger(self.name)
        sync_config = DictConfig('<%s configuration>' % self.name, config_options)
        self.user_groups = sync_config.get_list('user_groups', True)
        if self.user_groups is None:
            self.user_groups = []
        self.entitlement_groups = sync_config.get_list('entitlement_groups')
        self.directory_attributes = sync_config.get_list('directory_attributes', True)
        if self.directory_attributes is None:
            self.directory_attributes = []
        self.identity_types = sync_config.get_list('identity_types', True)
        if self.identity_types is None:
            self.identity_types = ['adobeID', 'enterpriseID', 'federatedID']

        api_config = sync_config.get_dict_config('api', True)
        api_builder = OptionsBuilder(api_config)
        api_builder.set_string_value('host', 'api.echosign.com')
        api_builder.require_string_value('key')
        api_builder.require_string_value('admin_email')
        self.api_config = api_builder.get_options()

    def run(self):
        """
        This function will run the sync connector
        """
        # get data to send through sync_users

    def get_directory_attributes(self):
        return self.directory_attributes
