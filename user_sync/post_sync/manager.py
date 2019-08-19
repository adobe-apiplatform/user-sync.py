import logging
from copy import deepcopy

import six

from user_sync.post_sync.connectors import get_connector

_SYNC_DATA_STORE = {}


class PostSyncManager:
    def __init__(self, post_sync_config):
        self.config = post_sync_config
        self.logger = logging.getLogger("post-sync")
        self.umapi_users = {}

        # Assemble to connector list
        self.connectors = [
            get_connector(m, c) for m, c in six.iteritems(self.config['modules'])
        ]

    def init_data_store(self, users):
        """
        just here so we can set some data.  initialization scheme still unknown
        data is stored in two ways -- the global data store and a class level variable
        ultimately one of these ways will be thrown out.  They share a common user
        creation process, so the data should be identical
        """

        for u in six.itervalues(users):
            # normalize key
            key = u['email'].lower()

            # One alternative
            # Store in instance scope, once-through
            self.umapi_users[key] = self.create_user(**u)

            # Other alternative
            # Storing in module scope, once-through to populate for now,
            # but can be populated from anywhere
            self.update_sync_data(key, **u)

    def run(self):
        """
        run each entry from the module dict from __init__
        :return:
        """
        for connector in self.connectors:
            self.logger.info("Running module " + connector.name)
            connector.run()
            self.logger.info("Finished running " + connector.name)

    @classmethod
    def create_user(cls, current_user=None, email_id=None, data_key='umapi_data', **new_data):

        if not current_user:
            current_user = cls._user_template()
            current_user['id'] = email_id or new_data['email']

        updated_user = deepcopy(current_user)
        for k, store_val in six.iteritems(updated_user[data_key]):
            if k not in new_data:
                continue
            updated_user[data_key][k] = new_data[k]
        updated_user['source_attributes'] = new_data.get('source_attributes')
        return updated_user

    @classmethod
    def update_sync_data(cls, email_id, data_key='umapi_data', add_groups=[], remove_groups=[], **kwargs):
        """
        Update (or insert) sync data for a given user
        :param str email_id:
        :param list add_groups:
        :param list remove_groups:
        :return:
        """

        global _SYNC_DATA_STORE
        email_key = email_id.lower()
        user_store_data = _SYNC_DATA_STORE.get(email_key)
        updated_store_data = cls.create_user(user_store_data, email_id, data_key, **kwargs)
        updated_store_data[data_key]['groups'] = list(set(updated_store_data[data_key]['groups']) | set(add_groups))
        updated_store_data[data_key]['groups'] = list(set(updated_store_data[data_key]['groups']) - set(remove_groups))

        _SYNC_DATA_STORE[email_key] = updated_store_data

    @staticmethod
    def _user_template():
        return {
            'id': '',
            'umapi_data': {
                'identity_type': None,
                'username': None,
                'domain': None,
                'email': None,
                'firstname': None,
                'lastname': None,
                'groups': [],
                'country': None,
            },
            'source_attributes': [],
            'sync_errors': []
        }
