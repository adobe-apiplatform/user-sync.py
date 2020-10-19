import pytest
import six

from user_sync.config.sign_sync import SignConfigLoader
from user_sync.connector.directory import DirectoryConnector
from user_sync.engine.sign import SignSyncEngine
from user_sync.connector.connector_sign import SignConnector
from user_sync.engine.umapi import AdobeGroup
from mock import patch
import logging


@pytest.fixture
def example_engine(sign_config_file):
    args = {'config_filename': sign_config_file}
    config = SignConfigLoader(args)
    rule_config = config.get_engine_options()
    return SignSyncEngine(rule_config)


@pytest.fixture
def directory_user():
    return {'directory_user': {'user@example.com':
                               {'type': 'federatedID',
                                'username': 'user@example.com',
                                'domain': 'example.com', 'email':
                                'user@example.com', 'firstname':
                                'Example', 'lastname':
                                'User',
                                'groups': set(),
                                'country': 'US'}}}

def test_load_users_and_groups(example_engine, example_user, directory_user):
    dc = DirectoryConnector

    user = {'directory_user': {'user@example.com': example_user}}

    def dir_user_replacement(groups, extended_attributes, all_users):
        return six.itervalues(user)

    dc.load_users_and_groups = dir_user_replacement
    mapping = {}
    adobeGroup = AdobeGroup('Group 1', 'primary')
    adobeGroups = []
    adobeGroups.append(adobeGroup)
    mapping['Sign Users'] = {'groups': adobeGroups}
    example_engine.read_desired_user_groups(mapping, dc)
    assert directory_user == user


def test_get_directory_user_key(example_engine, example_user):
    # user = {'user@example.com': example_user}
    # if the method is passed a dict with an email, it should return the email key
    assert example_engine.get_directory_user_key(
        example_user) == example_user['email']
    # if the user object passed in has no email value, it should return None
    assert example_engine.get_directory_user_key(
        {'': {'username': 'user@example.com'}}) is None


def test_insert_new_users(example_user):
    sign_engine = SignSyncEngine
    sign_connector = SignConnector
    umapi_user = example_user
    user_roles = ['NORMAL_USER']
    group_id = 'somemumbojumbohexadecimalstring'
    assignment_group = 'default group'
    insert_data = {
        "email": umapi_user['email'],
        "firstName": umapi_user['firstname'],
        "groupId": group_id,
        "lastName": umapi_user['lastname'],
        "roles": user_roles,
    }

    def insert_user(insert_data):
        pass
    sign_connector.insert_user = insert_user
    sign_engine.logger = logging.getLogger()
    sign_engine.insert_new_users(
        sign_engine, sign_connector, umapi_user, user_roles, group_id, assignment_group)
    assert True
    assert insert_data['email'] == 'user@example.com'


def test_deactivate_sign_users(example_user):
    sign_engine = SignSyncEngine
    sign_connector = SignConnector
    directory_users = {}
    directory_users['federatedID, example.user@signtest.com'] = {
        'email': 'example.user@signtest.com'}
    sign_users = {}
    sign_users['example.user@signtest.com'] = {
        'email': 'example.user@signtest.com', 'userId': 'somerandomhexstring'}

    def get_users():
        return sign_users

    def deactivate_user(insert_data):
        pass
    sign_connector.deactivate_user = deactivate_user
    sign_connector.get_users = get_users
    sign_engine.logger = logging.getLogger()
    org_name = 'primary'
    sign_engine.deactivate_sign_users(
        sign_engine, directory_users, sign_connector, org_name)
    assert True
    assert sign_users['example.user@signtest.com']['email'] == 'example.user@signtest.com'

