import logging
import os
import pytest
from six import StringIO
from user_sync import config
from user_sync.rules import RuleProcessor

@pytest.fixture
def fixture_dir():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 'fixture'))

@pytest.fixture
def cli_args():
    def _cli_args(args_in):
        """
        :param dict args:
        :return dict:
        """

        args_out = {}
        for k in config.ConfigLoader.invocation_defaults:
            args_out[k] = None
        for k, v in args_in.items():
            args_out[k] = v
        return args_out

    return _cli_args


@pytest.fixture
def log_stream():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    yield stream, logger
    handler.close()


@pytest.fixture
def rule_processor(caller_options):
    return RuleProcessor(caller_options)


@pytest.fixture
def caller_options():
    return {
        'adobe_group_filter': None,
        'after_mapping_hook': None,
        'default_country_code': 'US',
        'delete_strays': False,
        'directory_group_filter': None,
        'disentitle_strays': False,
        'exclude_groups': [],
        'exclude_identity_types': ['adobeID'],
        'exclude_strays': False,
        'exclude_users': [],
        'extended_attributes': None,
        'process_groups': True,
        'max_adobe_only_users': 200,
        'new_account_type': 'federatedID',
        'remove_strays': True,
        'strategy': 'sync',
        'stray_list_input_path': None,
        'stray_list_output_path': None,
        'test_mode': True,
        'update_user_info': False,
        'username_filter_regex': None,
        'adobe_only_user_action': ['remove'],
        'adobe_only_user_list': None,
        'adobe_users': ['all'],
        'config_filename': 'tests/fixture/user-sync-config.yml',
        'connector': 'ldap',
        'encoding_name': 'utf8',
        'user_filter': None,
        'users': None,
        'directory_connector_type': 'csv',
        'directory_connector_overridden_options': {
            'file_path': '../tests/fixture/remove-data.csv'},
        'adobe_group_mapped': False,
        'additional_groups': []}

@pytest.fixture
def mock_directory_user():
    return {
        'identity_type': 'federatedID',
        'username': 'nameless@example.com',
        'domain': 'example.com',
        'firstname': 'One',
        'lastname': 'Six',
        'email': 'nameless@example.com',
        'groups': ['All Sea of Carag'],
        'country': None,
        'member_groups': [],
        'source_attributes': {
            'email': 'nameless@example.com',
            'identity_type': None,
            'username': None,
            'domain': None,
            'givenName': 'One',
            'sn': 'Six',
            'c': 'US'}}

@pytest.fixture()
def mock_umapi_user():
    return  {
        'email': 'bsisko@example.com',
        'status': 'active',
        'groups': ['Group A', '_admin_Group A', 'Group A_1924484-provisioning'],
        'username': 'bsisko@example.com',
        'domain': 'example.com',
        'firstname': 'Benjamin',
        'lastname': 'Sisko',
        'country': 'CA',
        'type': 'federatedID'
    }