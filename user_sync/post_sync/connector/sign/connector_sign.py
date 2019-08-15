import logging

from user_sync.post_sync import PostSyncConnector

connector_class = "SignConnector"

logger = logging.getLogger('sign_sync')


class SignConnector(PostSyncConnector):

    def __init__(self, config):
        super().__init__()
        self.config = config.value

    def run(self):
        """
        This function will run the sync connector
        """
        # get data to send through sync_users
