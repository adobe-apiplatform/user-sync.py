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

    @classmethod
    def update_sync_data(cls, email_id, data_type, add_groups=[], remove_groups=[], **kwargs):
        """
        Update (or insert) sync data for a given user
        :param str email_id:
        :param list add_groups:
        :param list remove_groups:
        :param str data_type:
        :return:
        """
        valid_data_types = ['umapi']
        assert data_type in valid_data_types, "valid data_type options: {}".format(valid_data_types)

        global _SYNC_DATA_STORE

        email_key = email_id.lower()
        user_store_data = _SYNC_DATA_STORE.get(email_key)

        if user_store_data is None:
            user_store_data = cls._user_data_template()
            user_store_data['id'] = email_id

        data_key = '{}_data'.format(data_type)
        updated_store_data = deepcopy(user_store_data)
        for k, store_val in user_store_data[data_key].items():
            if k not in kwargs:
                continue
            updated_store_data[data_key][k] = kwargs[k]

        updated_store_data[data_key]['groups'] = list(set(updated_store_data[data_key]['groups']) | set(add_groups))
        updated_store_data[data_key]['groups'] = list(set(updated_store_data[data_key]['groups']) - set(remove_groups))

        _SYNC_DATA_STORE[email_key] = updated_store_data

    @staticmethod
    def _user_data_template():
        return {
            'id': user_key,
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
            'sync_errors': []
        }
