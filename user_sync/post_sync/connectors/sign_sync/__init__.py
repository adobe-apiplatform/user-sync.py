import logging
from user_sync.post_sync import PostSyncConnector
from user_sync.config import DictConfig, OptionsBuilder
from user_sync.rules import AdobeGroup
from .client import SignClient


class SignConnector(PostSyncConnector):
    name = 'sign_sync'

    def __init__(self, config_options):
        super().__init__()
        self.logger = logging.getLogger(self.name)
        sync_config = DictConfig('<%s configuration>' % self.name, config_options)
        self.user_groups = sync_config.get_list('user_groups', True)
        if self.user_groups is None:
            self.user_groups = []
        self.user_groups = self._groupify(self.user_groups)
        self.entitlement_groups = self._groupify(sync_config.get_list('entitlement_groups'))
        self.directory_attributes = sync_config.get_list('directory_attributes', True)
        if self.directory_attributes is None:
            self.directory_attributes = []
        self.identity_types = sync_config.get_list('identity_types', True)
        if self.identity_types is None:
            self.identity_types = ['adobeID', 'enterpriseID', 'federatedID']

        sign_orgs = sync_config.get_list('sign_orgs')
        self.clients = {}
        for sign_org_config in sign_orgs:
            sign_client = SignClient(sign_org_config)
            self.clients[sign_client.console_org] = sign_client

    def run(self, post_sync_data):
        """
        Run the Sign sync connector
        """
        for org_name, sign_client in self.clients.items():
            sign_users = sign_client.get_users()
            print(sign_users)

    def get_directory_attributes(self):
        return self.directory_attributes

    @staticmethod
    def _groupify(groups):
        return [AdobeGroup.create(g) for g in groups]
