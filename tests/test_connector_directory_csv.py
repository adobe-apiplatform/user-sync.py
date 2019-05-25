import os
import pytest
from user_sync.connector.directory_csv import *


@pytest.fixture
def default_caller_options():
    return {'email_column_name': 'email',
            'first_name_column_name': 'firstname',
            'last_name_column_name': 'lastname',
            'country_column_name': 'country',
            'groups_column_name': 'groups',
            'identity_type_column_name': 'type',
            'username_column_name': 'username',
            'domain_column_name': 'domain',
            'file_path': 'tests/fixture/csv_test.csv',
            'user_identity_type': 'federatedID'}


@pytest.fixture()
def csv_connector(default_caller_options):
    return CSVDirectoryConnector(default_caller_options)


def test_read_users(csv_connector):
    # expecting only three users information from Dakles_Information.csv
    # because other two users have invalid email addresses

    expected_result = {
        'dYennant@seaofcarag.com': {'identity_type': 'federatedID', 'username': 'dYennant@seaofcarag.com',
                                    'domain': None, 'firstname': None, 'lastname': 'Yennant',
                                    'email': 'dYennant@seaofcarag.com', 'groups': ['Daleks_Info'], 'country': 'US',
                                    'source_attributes': {'email': 'dYennant@seaofcarag.com', 'firstname': None,
                                                          'lastname': 'Yennant', 'country': 'US',
                                                          'groups': 'Daleks_Info', 'type': 'federatedID',
                                                          'username': None, 'domain': None, 'extraattribute': None}},
        'debmorgan@seaofcarag.com': {'identity_type': 'federatedID', 'username': 'debmorgan@seaofcarag.com',
                                     'domain': None, 'firstname': 'Debra', 'lastname': None,
                                     'email': 'debmorgan@seaofcarag.com', 'groups': ['Daleks_Info'], 'country': 'US',
                                     'source_attributes': {'email': 'debmorgan@seaofcarag.com', 'firstname': 'Debra',
                                                           'lastname': None, 'country': 'US', 'groups': 'Daleks_Info',
                                                           'type': 'federatedID', 'username': None, 'domain': None,
                                                           'extraattribute': None}},
        'ktownsnd@seaofcarag.com': {'identity_type': 'federatedID', 'username': 'ktownsnd@seaofcarag.com',
                                    'domain': None, 'firstname': 'Kevin', 'lastname': 'TownSnd',
                                    'email': 'ktownsnd@seaofcarag.com', 'groups': ['Daleks_Info'], 'country': 'US',
                                    'source_attributes': {'email': 'ktownsnd@seaofcarag.com', 'firstname': 'Kevin',
                                                          'lastname': 'TownSnd', 'country': 'US',
                                                          'groups': 'Daleks_Info', 'type': None, 'username': None,
                                                          'domain': None, 'extraattribute': None}},
        'pwizard@seaofcarag.com': {'identity_type': 'federatedID', 'username': 'pwizard@seaofcarag.com',
                                   'domain': 'seaofcarag.com', 'firstname': 'Park', 'lastname': 'Wizard',
                                   'email': 'pwizard@seaofcarag.com', 'groups': ['Daleks_Info'], 'country': 'US',
                                   'source_attributes': {'email': 'pwizard@seaofcarag.com', 'firstname': 'Park',
                                                         'lastname': 'Wizard', 'country': 'US', 'groups': 'Daleks_Info',
                                                         'type': 'federatedID', 'username': 'pwizard@seaofcarag.com',
                                                         'domain': 'seaofcarag.com', 'extraattribute': None}},
        'swizard@seaofcarag.com': {'identity_type': 'federatedID', 'username': 'swizard@seaofcarag.com',
                                   'domain': 'seaofcarag.com', 'firstname': 'Shark', 'lastname': 'Wizard',
                                   'email': 'swizard@seaofcarag.com', 'groups': ['Daleks_Info'], 'country': 'US',
                                   'source_attributes': {'email': 'swizard@seaofcarag.com', 'firstname': 'Shark',
                                                         'lastname': 'Wizard', 'country': 'US', 'groups': 'Daleks_Info',
                                                         'type': 'federatedID', 'username': 'swizard@seaofcarag.com',
                                                         'domain': 'seaofcarag.com', 'extraattribute': 'Adobe'}}}

    returned_users_list = csv_connector.read_users(csv_connector.options['file_path'], ['extraattribute'])

    assert expected_result == returned_users_list


def test_get_column_value(csv_connector):
    user = {'firstname': 'Dark', 'lastname': 'Wizard', 'email': 'dwizard@seaofcarag.com', 'country': None,
            'groups': 'Daleks_Info', 'type': 'federatedID', 'username': None, 'domain': None}

    assert csv_connector.get_column_value(user, 'email') == 'dwizard@seaofcarag.com'
    assert csv_connector.get_column_value(user, 'country') is None
    assert csv_connector.get_column_value(user, 'country1') is None
