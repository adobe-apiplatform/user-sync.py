import logging
import six
from copy import deepcopy
from .connectors import get_connector


class PostSyncManager:
    def __init__(self, post_sync_config):
        self.config = post_sync_config
        self.logger = logging.getLogger("post-sync")
        self.umapi_users = {}

        # Assemble to connector list
        self.connectors = [
            get_connector(m, c) for m, c in six.iteritems(self.config['modules'])
        ]

    def get_directory_attributes(self):
        attributes = set()
        for conn in self.connectors:
            attributes |= set(conn.get_directory_attributes())
        return attributes

    def run(self, post_sync_data):
        """
        run each entry from the module dict from __init__
        :return:
        """
        for connector in self.connectors:
            self.logger.info("Running module " + connector.name)
            connector.run(post_sync_data)
            self.logger.info("Finished running " + connector.name)


class PostSyncData:
    def __init__(self):
        self.umapi_data = {}
        self.source_attributes = {}

    def update_umapi_data(self, org_id, user_key, add_groups=[], remove_groups=[], **kwargs):
        """
        Update (or insert) sync data for a given user
        :param org_id:
        :param str user_key:
        :param list add_groups:
        :param list remove_groups:
        :return:
        """
        if org_id not in self.umapi_data:
            self.umapi_data[org_id] = {}

        umapi_data = self.umapi_data[org_id]
        user_store_data = umapi_data.get(user_key)

        if user_store_data is None:
            user_store_data = self._umapi_data_template()

        updated_store_data = deepcopy(user_store_data)
        for k in updated_store_data:
            if k not in kwargs:
                continue
            if k == 'groups':
                add_groups = list(set(add_groups) | set(kwargs[k]))
            else:
                updated_store_data[k] = kwargs[k]

        updated_store_data['groups'] |= set(add_groups)
        updated_store_data['groups'] -= set(remove_groups)

        self.umapi_data[org_id][user_key] = updated_store_data

    def update_source_attributes(self, user_key, source_attributes):
        self.source_attributes[user_key] = source_attributes

    @staticmethod
    def _umapi_data_template():
        return {
            'type': None,
            'username': None,
            'domain': None,
            'email': None,
            'firstname': None,
            'lastname': None,
            'groups': set(),
            'country': None,
        }
