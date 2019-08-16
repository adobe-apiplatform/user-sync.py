import logging
import six

from user_sync.post_sync import connector


class PostSyncManager:
    def __init__(self, post_sync_config, umapi_users):
        self.post_sync_config = post_sync_config
        self.logger = logging.getLogger("post-sync")
        self.connectors = []
        self.umapi_users = {}
        for k, u in six.iteritems(umapi_users):
            self.umapi_users[k] = self.create_umapi_user(k, u)

        for m, c in six.iteritems(self.post_sync_config['modules']):
            self.connectors.append(self.get_connector(m, c))

    def run(self):
        """
        run each entry from the module dict from __init__
        :return:
        """
        for connector in self.connectors:
            self.logger.info("Running module " + connector.name)
            connector.run()
            self.logger.info("Finished running " + connector.name)

    def get_connector(self, name, config):
        conn = connector.__CONNECTORS__[name]
        return conn(config)

    def create_umapi_user(self, user_key, user):

        return {
            'id': user_key,
            'umapi_data': {
                'identity_type': user.get('identity_type'),
                'username': user.get('username'),
                'domain': user.get('domain'),
                'email': user.get('email'),
                'firstname': user.get('firstname'),
                'lastname': user.get('lastname'),
                'groups': user.get('groups'),
                'country': user.get('country'),
            },
            'sync_errors': []
        }
