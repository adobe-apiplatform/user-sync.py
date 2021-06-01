import pytest
from mock import MagicMock

from user_sync.engine.umapi import UmapiTargetInfo, UmapiConnectors, RuleProcessor
from user_sync.connector.connector_umapi import Commands

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

    def test_create_umapi_user(self, rule_processor, mock_dir_user, mock_umapi_info):
        user = mock_dir_user
        rp = rule_processor

        key = rp.get_user_key(user['identity_type'], user['username'], user['domain'])
        rp.directory_user_by_user_key[key] = user
        rp.options['process_groups'] = True
        rp.push_umapi = True

        groups_to_add = {'Group A', 'Group C'}
        info = mock_umapi_info(None, {'Group A', 'Group B'})
        conn = MockUmapiConnector()
        rp.create_umapi_user(key, groups_to_add, info, conn)

        result = vars(conn.commands_sent)['do_list']
        result[0][1].pop('on_conflict')
        assert result[0] == ('create', {
            'email': user['email'],
            'first_name': user['firstname'],
            'last_name': user['lastname'],
            'country': user['country']})
        assert result[1] == ('remove_from_groups', {
            'groups': {'group b', 'group a'}})
        assert result[2] == ('add_to_groups', {
            'groups': {'Group C', 'Group A'}})

    def test_update_umapi_user(self, rule_processor, mock_dir_user, mock_umapi_user, get_mock_user_list):
        rp = rule_processor
        user = mock_dir_user
        mock_umapi_user['email'] = user['email']
        mock_umapi_user['username'] = user['username']
        mock_umapi_user['domain'] = user['domain']
        mock_umapi_user['type'] = user['identity_type']

        def update(up_user, up_attrs):
            group_add = set()
            group_rem = set()
            conn = MockUmapiConnector()
            info = UmapiTargetInfo(None)
            user_key = rp.get_user_key(up_user['identity_type'], up_user['username'], up_user['domain'])
            rp.directory_user_by_user_key[user_key] = up_user
            rp.update_umapi_user(info, user_key, conn, up_attrs, group_add, group_rem, mock_umapi_user)
            assert user_key in rp.updated_user_keys
            return vars(conn.commands_sent)

        up_attrs = {
            'firstname': user['firstname'],
            'lastname': user['lastname']}

        result = update(user, up_attrs)
        assert result == {
            'identity_type': user['identity_type'],
            'email': user['email'],
            'username': user['username'],
            'domain': user['domain'],
            'do_list': [('update', {
                'first_name': user['firstname'],
                'last_name': user['lastname']})]}

        user['username'] = 'different@example.com'
        result = update(user, up_attrs)
        assert result['username'] == user['email']

        user['email'] = 'different@example.com'
        up_attrs = {
            'email': user['email']}
        result = update(user, up_attrs)

        assert result == {
            'identity_type': user['identity_type'],
            'email': user['email'],
            'username': user['username'],
            'domain': user['domain'],
            'do_list': [('update', {
                'email': 'different@example.com',
                'username': user['username']})]}

    def test_create_umapi_commands_for_directory_user(self, rule_processor, mock_dir_user):
        rp = rule_processor
        user = mock_dir_user

        def get_commands(user, update_option='ignoreIfAlreadyExists'):
            attributes = rp.get_user_attributes(user)
            attributes['country'] = user['country']
            attributes['option'] = update_option
            commands = Commands(user['identity_type'], user['email'], user['username'], user['domain'])
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
        commands.update_user({
            "email": user['email'],
            "username": user['username']})
        commands.username = user['email']
        result = rp.create_umapi_commands_for_directory_user(user)
        assert vars(result) == vars(commands)

        # test console trusted
        user['username'] = 'different@example.com'
        commands = get_commands(user)
        commands.username = user['email']
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

    def test_get_user_attribute_difference(self, rule_processor, mock_dir_user, mock_umapi_user):
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