import logging

from user_sync.post_sync import PostSyncConnector

class SignConnector(PostSyncConnector):
    name = 'sign_sync'

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(self.name)

        # All the wonderful init things

    def run(self):
        """
        This function will run the sync connector
        """
        # get data to send through sync_users
