import csv
import re

import mock
import pytest
import yaml
from mock import MagicMock

from tests.util import compare_iter
from user_sync.connector.connector_umapi import Commands
from user_sync.engine.common import AdobeGroup
from user_sync.engine.umapi import UmapiTargetInfo, UmapiConnectors, RuleProcessor, MultiIndex


@pytest.fixture
def rule_processor():
    return RuleProcessor({})


@pytest.fixture()
def mock_umapi_connectors():
    def _mock_umapi_connectors(*args):
        return UmapiConnectors(
            MockUmapiConnector(),
            {a: MockUmapiConnector(name=a) for a in args})

    return _mock_umapi_connectors


@pytest.fixture()
def mock_umapi_info():
    def _mock_umapi_info(name=None, groups=[]):
        mock_umapi_info = UmapiTargetInfo(name)
        for g in groups:
            mock_umapi_info.add_mapped_group(g)
        return mock_umapi_info

    return _mock_umapi_info


class MockUmapiConnector(MagicMock):
    class MockActionManager:
        def get_statistics(self):
            return 10, 2

    def __init__(self, name='', options={}, *args, **kwargs):
        super(MockUmapiConnector, self).__init__(*args, **kwargs)
        self.name = 'umapi' + name
        self.trusted = False
        self.options = options
        self.action_manager = MockUmapiConnector.MockActionManager()
        self.commands_sent = None
        self.users = {}

    def send_commands(self, commands):
        self.commands_sent = commands

    def get_action_manager(self):
        return self.action_manager

    def iter_users(self):
        return self.users


def test_is_umapi_user_excluded(rule_processor):
    in_primary_org = True
    rule_processor.exclude_identity_types = ['adobeID']
    user_key = 'adobeID,adobe.user@example.com,,'
    current_groups = {'default acrobat pro dc configuration', 'one', '_admin_group a'}
    assert rule_processor.is_umapi_user_excluded(in_primary_org, user_key, current_groups)

    user_key = 'federatedID,adobe.user@example.com,,'
    rule_processor.exclude_groups = {'one'}
    assert rule_processor.is_umapi_user_excluded(in_primary_org, user_key, current_groups)

    user_key = 'federatedID,adobe.user@example.com,,'
    rule_processor.exclude_groups = set()
    compiled_expression = re.compile(r'\A' + "adobe.user@example.com" + r'\Z', re.IGNORECASE)
    rule_processor.exclude_users = {compiled_expression}
    assert rule_processor.is_umapi_user_excluded(in_primary_org, user_key, current_groups)


def test_create_umapi_user(rule_processor, mock_dir_user, mock_umapi_info):
    user = mock_dir_user
    rp = rule_processor

    def progress_func(*_):
        pass

    rp.logger.progress = progress_func

    key = rp.get_user_key(user['identity_type'], user['username'], user['domain'])
    rp.directory_user_index = MultiIndex(data=[user], key_names=['email', 'username'])
    rp.options['process_groups'] = True
    rp.push_umapi = True

    groups_to_add = {'Group A', 'Group C'}
    info = mock_umapi_info(None, {'Group A', 'Group B'})
    conn = MockUmapiConnector()
    commands = [rp.create_umapi_user(key, groups_to_add, info, True)]
    rp.execute_commands(commands, conn)

    result = vars(conn.commands_sent)['do_list']
    result[0][1].pop('on_conflict')
    assert result[0] == ('create', {
        'email': user['email'],
        'firstname': user['firstname'],
        'lastname': user['lastname'],
        'country': user['country'],
        'id_type': user['identity_type'],
    })
    assert result[1] == ('remove_from_groups', {
        'groups': {'group b', 'group a'}})
    assert result[2] == ('add_to_groups', {
        'groups': {'Group C', 'Group A'}})


def test_update_umapi_user(rule_processor, mock_dir_user, mock_umapi_user):
    rp = rule_processor
    user = mock_dir_user
    mock_umapi_user['email'] = user['email']
    mock_umapi_user['username'] = user['username']
    mock_umapi_user['domain'] = user['domain']
    mock_umapi_user['type'] = user['identity_type']

    def progress_func(*_):
        pass

    rp.logger.progress = progress_func

    def update(up_user, up_attrs):
        group_add = set()
        group_rem = set()
        conn = MockUmapiConnector()
        info = UmapiTargetInfo(None)
        user_key = rp.get_user_key(up_user['identity_type'], up_user['username'], up_user['domain'])
        rp.directory_user_index = MultiIndex(data=[up_user], key_names=['email', 'username'])
        commands = [rp.update_umapi_user(info, user_key, up_attrs, group_add, group_rem, mock_umapi_user)]
        rp.execute_commands(commands, conn)
        assert user_key in rp.updated_user_keys
        return vars(conn.commands_sent)

    up_attrs = {
        'firstname': user['firstname'],
        'lastname': user['lastname']}

    result = update(user, up_attrs)
    assert result == {
        'user': user['email'],
        'domain': user['domain'],
        'do_list': [('update', {
            'firstname': user['firstname'],
            'lastname': user['lastname']})]}

    user['username'] = 'different@example.com'
    result = update(user, up_attrs)
    assert result['user'] == user['email']

    user['email'] = 'different@example.com'
    up_attrs = {
        'email': user['email']}
    result = update(user, up_attrs)

    assert result == {
        'user': user['email'],
        'domain': user['domain'],
        'do_list': [('update', {
            'email': 'different@example.com',
            'username': user['username']})]}


def test_create_umapi_commands_for_directory_user(rule_processor, mock_dir_user):
    rp = rule_processor
    user = mock_dir_user

    def get_commands(user, update_option='ignoreIfAlreadyExists'):
        attributes = rp.get_create_attributes(user)
        attributes['country'] = user['country']
        attributes['option'] = update_option
        attributes['id_type'] = user['identity_type']
        commands = Commands(user['username'], user['domain'])
        commands.add_user(attributes)
        return commands

    # simple case
    commands = get_commands(user)
    result = rp.create_umapi_commands_for_directory_user(user)
    assert vars(result) == vars(commands)

    # test do_update
    commands = get_commands(user, 'updateIfAlreadyExists')
    result = rp.create_umapi_commands_for_directory_user(user, do_update=True)
    assert vars(result) == vars(commands)

    # test username format
    user['username'] = 'nosymbol'
    commands = get_commands(user)
    result = rp.create_umapi_commands_for_directory_user(user)
    assert vars(result) == vars(commands)

    # test username format
    user['username'] = 'different@example.com'
    commands = get_commands(user)
    result = rp.create_umapi_commands_for_directory_user(user)
    assert vars(result) == vars(commands)

    # test console trusted
    user['username'] = 'different@example.com'
    commands = get_commands(user)
    result = rp.create_umapi_commands_for_directory_user(user, console_trusted=True)
    assert vars(result) == vars(commands)

    # Default Country Code as None and Id Type as federatedID. Country as None in user
    rp.options['default_country_code'] = None
    user['country'] = None
    result = rp.create_umapi_commands_for_directory_user(user)
    assert result is None

    # Default Country Code as None with Id Type as enterpriseID. Country as None in user
    rp.options['default_country_code'] = None
    user['identity_type'] = 'enterpriseID'
    result = rp.create_umapi_commands_for_directory_user(user)
    user['country'] = 'UD'
    commands = get_commands(user)
    assert vars(result) == vars(commands)

    # Having Default Country Code with value 'US'. Country as None in user.
    rp.options['default_country_code'] = 'US'
    user['country'] = None
    result = rp.create_umapi_commands_for_directory_user(user)
    user['country'] = 'US'
    commands = get_commands(user)
    assert vars(result) == vars(commands)

    # Country as 'CA' in user
    user['country'] = 'CA'
    result = rp.create_umapi_commands_for_directory_user(user)
    commands = get_commands(user)
    assert vars(result) == vars(commands)


def test_get_user_attribute_difference(rule_processor, mock_dir_user, mock_umapi_user):
    directory_user_mock_data = mock_dir_user
    umapi_users_mock_data = mock_umapi_user
    umapi_users_mock_data['firstname'] = 'Adobe'
    umapi_users_mock_data['lastname'] = 'Username'
    umapi_users_mock_data['email'] = 'adobe.username@example.com'

    expected = {
        'email': mock_dir_user['email'],
        'firstname': mock_dir_user['firstname'],
        'lastname': mock_dir_user['lastname']
    }

    assert expected == rule_processor.get_user_attribute_difference(
        directory_user_mock_data, umapi_users_mock_data)

    # test with no change
    assert rule_processor.get_user_attribute_difference(
        umapi_users_mock_data, umapi_users_mock_data) == {}


def test_get_directory_user_key(rule_processor):
    mock_directory_user_dict = {
        'email': 'email@example.com',
        'username': 'username@example.com',
        'domain': 'example.com',
        'identity_type': 'federatedID'
    }
    actual_result = rule_processor.get_directory_user_key(mock_directory_user_dict)
    assert actual_result == 'federatedID,username@example.com,,email@example.com'


def test_get_umapi_user_key(rule_processor):
    mock_umapi_user_dict = {
        'email': 'email@example.com',
        'username': 'username@example.com',
        'domain': 'example.com',
        'type': 'federatedID'
    }

    actual_result = rule_processor.get_umapi_user_key(mock_umapi_user_dict)
    assert actual_result == 'federatedID,username@example.com,,email@example.com'


def test_get_user_key(rule_processor):
    key = rule_processor.get_user_key("federatedID", "username@example.com", "example.com", "email@example.com")
    assert key == 'federatedID,username@example.com,,email@example.com'

    key = rule_processor.get_user_key("federatedID", "username", "example.com", "email@example.com")
    assert key == 'federatedID,username,example.com,email@example.com'

    assert not rule_processor.get_user_key(None, "wriker@example.com", "wriker@example.com", "example.com")
    assert not rule_processor.get_user_key("federatedID", None, "wriker@example.com")


def test_parse_user_key(rule_processor):
    parsed_user_key = rule_processor.parse_user_key("federatedID,test_user@email.com,")
    assert parsed_user_key == ['federatedID', 'test_user@email.com', '']

    domain_parsed_key = rule_processor.parse_user_key("federatedID,test_user,email.com")
    assert domain_parsed_key == ['federatedID', 'test_user', 'email.com']


def test_get_username_from_user_key(rule_processor):
    with mock.patch('user_sync.engine.umapi.RuleProcessor.parse_user_key') as parse:
        parse.return_value = ['federatedID', 'test_user@email.com', '']
        username = rule_processor.get_username_from_user_key("federatedID,test_user@email.com,")
        assert username == 'test_user@email.com'

def test_read_desired_user_groups_basic(rule_processor, mock_dir_user):
    rp = rule_processor
    mock_dir_user['groups'] = ['Group A', 'Group B']

    directory_connector = mock.MagicMock()
    directory_connector.load_users_and_groups.return_value = [mock_dir_user]
    mappings = {
        'Group A': [AdobeGroup.create('Console Group')]}
    rp.read_desired_user_groups(mappings, directory_connector)

    # Assert the security group and adobe group end up in the correct scope
    assert "Group A" in rp.after_mapping_hook_scope['source_groups']
    assert "Console Group" in rp.after_mapping_hook_scope['target_groups']

    # Assert the user group updated in umapi info
    assert 'console group' in rp.umapi_info_by_name[None].get_desired_groups(email=mock_dir_user['email'], username=mock_dir_user['username'])['desired_groups']
    assert mock_dir_user['email'] == rp.filtered_directory_user_index.data[0]['email']

@mock.patch('user_sync.helper.CSVAdapter.read_csv_rows')
def test_read_stray_key_map(csv_reader, rule_processor):
    csv_mock_data = [
        {
            'type': 'adobeID',
            'email': 'removeuser2@example.com',
            'domain': 'example.com'
        },
        {
            'type': 'federatedID',
            'email': 'removeuser@example.com',
            'domain': 'example.com'
        },
        {
            'type': 'enterpriseID',
            'email': 'removeuser3@example.com',
            'domain': 'example.com'
        },
    ]

    csv_reader.return_value = csv_mock_data
    rule_processor.read_stray_key_map('')
    actual_value = rule_processor.stray_key_map
    expected_value = {
        None: {
            'adobeID,removeuser2@example.com,,removeuser2@example.com': None,
            'federatedID,removeuser@example.com,,removeuser@example.com': None,
            'enterpriseID,removeuser3@example.com,,removeuser3@example.com': None,
        }
    }

    assert expected_value == actual_value

    # Added secondary umapi value
    csv_mock_data = [
        {
            'type': 'adobeID',
            'email': 'remove@example.com',
            'domain': 'sample.com',
            'umapi': 'secondary'},
        {
            'type': 'federatedID',
            'email': 'removeuser@example.com'},
        {
            'type': 'enterpriseID',
            'email': 'removeuser3@example.com',
            'domain': 'example.com'}

    ]
    csv_reader.return_value = csv_mock_data
    rule_processor.read_stray_key_map('')
    actual_value = rule_processor.stray_key_map
    expected_value = {
        'secondary': {
            'adobeID,remove@example.com,,remove@example.com': None
        },
        None: {
            'federatedID,removeuser@example.com,,removeuser@example.com': None,
            'enterpriseID,removeuser3@example.com,,removeuser3@example.com': None,
            'adobeID,removeuser2@example.com,,removeuser2@example.com': None
        }
    }
    assert expected_value == actual_value


def test_write_stray_key_map(rule_processor, tmpdir):
    tmp_file = str(tmpdir.join('strays_test.csv'))

    rule_processor.stray_list_output_path = tmp_file
    rule_processor.stray_key_map = {
        'secondary': {
            'adobeID,remoab@example.com,,remoab@example.com': set(),
            'enterpriseID,adobe.user3@example.com,,adobe.user3@example.com': set(), },
        None: {
            'enterpriseID,adobe.user1@example.com,,adobe.user1@example.com': set(),
            'federatedID,adobe.user2@example.com,,adobe.user2@example.com': set()
        }}

    rule_processor.write_stray_key_map()
    with open(tmp_file, 'r') as our_file:
        reader = csv.reader(our_file)
        actual = list(reader)
        expected = [['type', 'email', 'domain', 'umapi'],
                    ['adobeID', 'remoab@example.com', '', 'secondary'],
                    ['enterpriseID', 'adobe.user3@example.com', '', 'secondary'],
                    ['enterpriseID', 'adobe.user1@example.com', '', ''],
                    ['federatedID', 'adobe.user2@example.com', '', '']]
        assert compare_iter(actual, expected)


def test_log_after_mapping_hook_scope(rule_processor, log_stream):
    rp = rule_processor
    stream, logger = log_stream

    def compare_attr(text, target):
        s = yaml.safe_load(re.search('{.+}', text).group())
        for attr in s:
            if s[attr] != 'None':
                assert s[attr] == target[attr]

    state = {
        'source_attributes': {
            'email': 'bsisko@example.com',
            'identity_type': None,
            'username': None,
            'domain': None,
            'givenName': 'Benjamin',
            'sn': 'Sisko',
            'c': 'CA'},
        'source_groups': set(),
        'target_attributes': {
            'email': 'bsisko@example.com',
            'username': 'bsisko@example.com',
            'domain': 'example.com',
            'firstname': 'Benjamin',
            'lastname': 'Sisko',
            'country': 'CA'},
        'target_groups': set(),
        'log_stream': logger,
        'hook_storage': None
    }

    rp.logger = logger
    rp.after_mapping_hook_scope = state
    rp.log_after_mapping_hook_scope(before_call=True)
    stream.flush()
    x = stream.getvalue().split('\n')

    assert len(x[2]) < 32
    assert len(x[4]) < 32
    compare_attr(x[1], state['source_attributes'])
    compare_attr(x[3], state['target_attributes'])

    state['target_groups'] = {'One'}
    state['target_attributes']['firstname'] = 'John'
    state['source_attributes']['sn'] = 'David'
    state['source_groups'] = {'One'}

    rp.after_mapping_hook_scope = state
    rp.log_after_mapping_hook_scope(after_call=True)
    stream.flush()
    x = stream.getvalue().split('\n')

    assert re.search('(Target groups, after).*(One)', x[6])
    compare_attr(x[5], state['target_attributes'])


def test_targetinfo_add_mapped_group():
    umapi_target_info = UmapiTargetInfo("")
    umapi_target_info.add_mapped_group("All Students")
    assert "all students" in umapi_target_info.mapped_groups
    assert "All Students" in umapi_target_info.non_normalize_mapped_groups

def test_targetinfo_add_additional_group():
    umapi_target_info = UmapiTargetInfo("")
    umapi_target_info.add_additional_group('old_name', 'new_name')
    assert umapi_target_info.additional_group_map['old_name'][0] == 'new_name'

def test_targetinfo_add_desired_group_for():
    umapi_target_info = UmapiTargetInfo(None)
    umapi_target_info.add_desired_group_for('federatedID', 'example.com', 'user@example.com', 'user@example.com', 'group_name')
    assert 'group_name' in umapi_target_info.get_desired_groups('user@example.com', 'user@example.com')['desired_groups']


@pytest.fixture
def test_data():
    return [{
        "email": "user1@example.com",
        "username": "user1.un@example.com",
        "firstname": "Test",
        "lastname": "User 001",
    },{
        "email": "user2@example.com",
        "username": "user2.un@example.com",
        "firstname": "Test",
        "lastname": "User 002",
    },{
        "email": "user3@example.com",
        "username": "user3.un@example.com",
        "firstname": "Test",
        "lastname": "User 003",
    }]
 

def test_new_multi_index(test_data):
    """Construct valid MultiIndex with no errors"""
    user_index = MultiIndex(data=test_data, key_names=['email', 'username'])
    assert user_index.data == test_data
    assert user_index.key_names == ['email', 'username']
    assert user_index.index['email'] == {'user1@example.com': 0, 'user2@example.com': 1, 'user3@example.com': 2}
    assert user_index.index['username'] == {'user1.un@example.com': 0, 'user2.un@example.com': 1, 'user3.un@example.com': 2}


def test_new_multi_index_keyerr(test_data):
    """MultiIndex data must be complete"""
    del test_data[1]['email']

    with pytest.raises(KeyError):
        MultiIndex(data=test_data, key_names=['email', 'username'])


def test_multi_index_retrieve(test_data):
    """Ensure we get one record from MultiIndex"""
    user_index = MultiIndex(data=test_data, key_names=['email', 'username'])
    # get a single user with exact email/username match
    user = user_index.get(email='user3@example.com', username='user3.un@example.com')
    assert user['firstname'] == 'Test'
    assert user['lastname'] == 'User 003'

    # get a single user where email matches but not username
    user = user_index.get(email='user2@example.com', username='user2@example.com')
    assert user['firstname'] == 'Test'
    assert user['lastname'] == 'User 002'

    # get a single record with a single key
    user = user_index.get(email='user1@example.com')
    assert user['firstname'] == 'Test'
    assert user['lastname'] == 'User 001'


def test_multi_index_retrieve_none(test_data):
    user_index = MultiIndex(data=test_data, key_names=['email', 'username'])
    result = user_index.get(email='user4@example.com', username='user4.un@example.com')
    assert result is None


def test_multi_index_nonexistent_key(test_data):
    user_index = MultiIndex(data=test_data, key_names=['email', 'username'])
    with pytest.raises(KeyError):
        user_index.get(foobar='user1@example.com')


def test_multi_index_add_record(test_data):
    user_index = MultiIndex(data=test_data, key_names=['email', 'username'])
    user_index.add({
        'email': 'user4@example.com',
        'username': 'user4.un@example.com',
        'firstname': 'Test',
        'lastname': 'User 004',
    })

    user = user_index.get(email='user4@example.com', username='user4.un@example.com')
    assert user['firstname'] == 'Test'
    assert user['lastname'] == 'User 004'


def test_multi_index_add_record_err(test_data):
    user_index = MultiIndex(data=test_data, key_names=['email', 'username'])
    with pytest.raises(KeyError):
        user_index.add({
            'email': 'user4@example.com',
            'firstname': 'Test',
            'lastname': 'User 004',
        })


def test_multi_index_update(test_data):
    user_index = MultiIndex(data=test_data, key_names=['email', 'username'])
    user = test_data[0].copy()
    user['firstname'] = 'Test Updated'
    user['lastname'] = 'User 001 Updated'

    user_index.update(user, email=user['email'], username=user['username'])

    user = user_index.get(email=user['email'], username=user['username'])
    assert user['firstname'] == 'Test Updated'
    assert user['lastname'] == 'User 001 Updated'
