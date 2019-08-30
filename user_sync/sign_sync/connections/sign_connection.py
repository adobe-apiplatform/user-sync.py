import requests
import json
import yaml
import logging
from user_sync.error import AssertionException

logger = logging.getLogger('sign_sync')


class Sign:
    _endpoint_template = 'api/rest/{}/'

    def __init__(self, config_filename):
        self.sign_users = self.get_sign_users()
        self.default_group = self.get_sign_group()['Default Group']

    class SignDecorators:
        @classmethod
        def exception_catcher(cls, func):
            def wrapper(*args, **kwargs):
                try:
                    res = func(*args, **kwargs)
                    return res
                except requests.exceptions.HTTPError as http_error:
                    logger.error("-- HTTP ERROR: {} --".format(http_error))
                    raise AssertionException('sign sync failed')
                except requests.exceptions.ConnectionError as conn_error:
                    logger.error("-- ERROR CONNECTING -- {}".format(conn_error))
                    raise AssertionException('sign sync failed')
                except requests.exceptions.Timeout as timeout_error:
                    logger.error("-- TIMEOUT ERROR: {} --".format(timeout_error))
                    raise AssertionException('sign sync failed')
                except requests.exceptions.RequestException as error:
                    logger.error("-- ERROR: {} --".format(error))
                    raise AssertionException('sign sync failed')

            return wrapper
