from copy import deepcopy
import logging

import user_sync.post_sync.connector.sign.connector_sign

_SYNC_DATA_STORE = {}

_modules = {"sign_sync": user_sync.post_sync.connector.sign.connector_sign.SignConnector}


class Manager:
    def __init__(self, config):
        self.config = config
        self.connectors = []
        self.post_sync_modules = config['post_sync_modules']
        for module in self.post_sync_modules:
            self.connectors.append(_modules[module](self.config[module]))
        self.run()

    def run(self):
        """
        run each entry from the module dict from __init__
        :return:
        """
        for each in self.connectors:
            logging.info("running module" + str(each))
            each.run()
            logging.info("finished running " + str(each))

    def update_sync_data(self, email_id, data_type, add_groups=[], remove_groups=[], **kwargs):
        """
        Update (or insert) sync data for a given user
        :param str email_id:
        :param list add_groups:
        :param list remove_groups:
        :param str data_type:
        :return:
        """
        valid_data_types = ['umapi', 'directory']
        assert data_type in valid_data_types, "valid data_type options: {}".format(valid_data_types)

        global _SYNC_DATA_STORE

        email_key = email_id.lower()

        user_store_data = _SYNC_DATA_STORE.get(email_key)

        if user_store_data is None:
            user_store_data = _user_data_template()
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

    def _user_data_template(self):
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
            'directory_data': {
                'identity_type': None,
                'username': None,
                'domain': None,
                'email': None,
                'firstname': None,
                'lastname': None,
                'groups': [],
                'country': None,
                'raw_data': {}
            },
            'sync_errors': []
        }
