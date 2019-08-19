import re
import mock
import pytest
import yaml
from user_sync.rules import RuleProcessor, AdobeGroup, UmapiTargetInfo


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
def umapi_target_info():
    return UmapiTargetInfo("")


@mock.patch('user_sync.helper.CSVAdapter.read_csv_rows')
def test_stray_key_map(csv_reader, rule_processor):
    csv_mock_data = [{
                         'type': 'adobeID',
                         'username': 'removeuser2@example.com',
                         'domain': 'example.com'},
                     {
                         'type': 'federatedID',
                         'username': 'removeuser@example.com',
                         'domain': 'example.com'},
                     {
                         'type': 'enterpriseID',
                         'username': 'removeuser3@example.com',
                         'domain': 'example.com'}]
    csv_reader.return_value = csv_mock_data
    rule_processor.read_stray_key_map('')
    actual_value = rule_processor.stray_key_map
    expected_value = {
        None: {
            'federatedID,removeuser@example.com,': None,
            'enterpriseID,removeuser3@example.com,': None,
            'adobeID,removeuser2@example.com,': None}}

    assert expected_value == actual_value

    # Added secondary umapi value
    csv_mock_data = [{
                         'type': 'adobeID',
                         'username': 'remo@sample.com',
                         'domain': 'sample.com',
                         'umapi': 'secondary'},
                     {
                         'type': 'federatedID',
                         'username': 'removeuser@example.com'},
                     {
                         'type': 'enterpriseID',
                         'username': 'removeuser3@example.com',
                         'domain': 'example.com'}]
    csv_reader.return_value = csv_mock_data
    rule_processor.read_stray_key_map('')
    actual_value = rule_processor.stray_key_map
    expected_value = {
        'secondary': {
            'adobeID,remo@sample.com,': None},
        None: {
            'federatedID,removeuser@example.com,': None,
            'enterpriseID,removeuser3@example.com,': None,
            'adobeID,removeuser2@example.com,': None}}
    assert expected_value == actual_value


def test_get_user_attribute_difference(rule_processor):
    umapi_users_mock_data = {
        'email': 'adobe.username@example.com',
        'status': 'active',
        'username': 'adobe.username@example.com',
        'domain': 'example.com',
        'firstname': 'Adobe',
        'lastname': 'Username',
        'country': 'US',
        'type': 'federatedID'}

    # Updated user's email, firstname and lastname
    directory_user_mock_data = {
        'identity_type': 'federatedID',
        'username': 'adobeupdate.username2@example.com',
        'domain': 'example.com',
        'firstname': 'Adobeupdate',
        'lastname': 'Username2',
        'email': 'adobeupdate.username2@example.com',
        'groups': ['All Sea of Carag'],
        'country': 'US',
        'member_groups': [],
        'source_attributes': {
            'email': 'adobeupdate.username2@example.com',
            'identity_type': None,
            'username': None,
            'domain': None,
            'givenName': 'Adobeupdate',
            'sn': 'Username2',
            'c': 'US'}}

    actual_difference_value = rule_processor.get_user_attribute_difference(directory_user_mock_data,
                                                                           umapi_users_mock_data)
    expected_difference_value = {
        'email': 'adobeupdate.username2@example.com',
        'firstname': 'Adobeupdate',
        'lastname': 'Username2'}
    assert expected_difference_value == actual_difference_value
    # test with no change
    actual_difference_value = rule_processor.get_user_attribute_difference(umapi_users_mock_data, umapi_users_mock_data)
    assert actual_difference_value == {}


def test_log_after_mapping_hook_scope(log_stream):
    stream, logger = log_stream

    def compare_attr(text, target):
        s = yaml.safe_load(re.search('{.+}', text).group())
        for attr in s:
            if s[attr] != 'None':
                assert s[attr] == target[attr]

    state = {
        'source_attributes': {
            'email': 'bsisko@seaofcarag.com',
            'identity_type': None,
            'username': None,
            'domain': None,
            'givenName': 'Benjamin',
            'sn': 'Sisko',
            'c': 'CA'},
        'source_groups': set(),
        'target_attributes': {
            'email': 'bsisko@seaofcarag.com',
            'username': 'bsisko@seaofcarag.com',
            'domain': 'seaofcarag.com',
            'firstname': 'Benjamin',
            'lastname': 'Sisko',
            'country': 'CA'},
        'target_groups': set(),
        'log_stream': logger,
        'hook_storage': None}

    ruleprocessor = RuleProcessor({})
    ruleprocessor.logger = logger
    ruleprocessor.after_mapping_hook_scope = state
    ruleprocessor.log_after_mapping_hook_scope(before_call=True)
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

    ruleprocessor.after_mapping_hook_scope = state
    ruleprocessor.log_after_mapping_hook_scope(after_call=True)
    stream.flush()
    x = stream.getvalue().split('\n')

    assert re.search('(Target groups, after).*(One)', x[6])
    compare_attr(x[5], state['target_attributes'])


def test_get_username_from_user_key(rule_processor):
    with mock.patch('user_sync.rules.RuleProcessor.parse_user_key') as parse:
        parse.return_value = ['federatedID', 'test_user@email.com', '']
        username = rule_processor.get_username_from_user_key("federatedID,test_user@email.com,")
        assert username == 'test_user@email.com'


def test_parse_user_key(rule_processor):
    parsed_user_key = rule_processor.parse_user_key("federatedID,test_user@email.com,")
    assert parsed_user_key == ['federatedID', 'test_user@email.com', '']

    domain_parsed_key = rule_processor.parse_user_key("federatedID,test_user,email.com")
    assert domain_parsed_key == ['federatedID', 'test_user', 'email.com']


def test_add_mapped_group(umapi_target_info):
    umapi_target_info.add_mapped_group("All Students")
    assert "all students" in umapi_target_info.mapped_groups
    assert "All Students" in umapi_target_info.non_normalize_mapped_groups


def test_add_additional_group(umapi_target_info):
    umapi_target_info.add_additional_group('old_name', 'new_name')
    assert umapi_target_info.additional_group_map['old_name'][0] == 'new_name'


def test_add_desired_group_for(umapi_target_info):
    with mock.patch("user_sync.rules.UmapiTargetInfo.get_desired_groups") as mock_desired_groups:
        mock_desired_groups.return_value = None
        umapi_target_info.add_desired_group_for('user_key', 'group_name')
        assert umapi_target_info.desired_groups_by_user_key['user_key'] == {'group_name'}


def test_create():
    with mock.patch("user_sync.rules.AdobeGroup._parse") as parse:
        parse.return_value = ('group_name', None)
        AdobeGroup.create('this')
        assert ('group_name', None) in AdobeGroup.index_map


def test_parse():
    result = AdobeGroup._parse('qualified_name')
    assert result == ('qualified_name', None)

def test_add_stray(rule_processor):
    user_key_mock_data = 'federatedID,rules.user@seaofcarag.com,'
    removed_groups_mock_data = {'aishtest'}
    rule_processor.stray_key_map = {None: {}}
    rule_processor.add_stray(None, user_key_mock_data, removed_groups_mock_data)
    assert rule_processor.stray_key_map[None][user_key_mock_data] == removed_groups_mock_data


def test_process_stray(rule_processor, log_stream):
    stream, logger = log_stream
    rule_processor.logger = logger
    with mock.patch("user_sync.rules.RuleProcessor.manage_strays"):
        rule_processor.stray_key_map = {None: {'federatedID,testuser2000@example.com,': set()}}
        rule_processor.process_strays({})

        stream.flush()
        actual_logger_output = stream.getvalue()
        assert "Processing Adobe-only users..." in actual_logger_output

    rule_processor.options["max_adobe_only_users"] = 0
    rule_processor.process_strays({})
    stream.flush()
    actual_logger_output = stream.getvalue()
    assert "Unable to process Adobe-only users" in actual_logger_output
    assert rule_processor.action_summary["primary_strays_processed"] == 0

    rule_processor.primary_user_count = 10
    rule_processor.excluded_user_count = 1
    rule_processor.options["max_adobe_only_users"] = "5%"
    rule_processor.process_strays({})
    stream.flush()
    actual_logger_output = stream.getvalue()
    assert "Unable to process Adobe-only users" in actual_logger_output
    assert rule_processor.action_summary["primary_strays_processed"] == 0

    with mock.patch("user_sync.rules.RuleProcessor.manage_strays"):
        rule_processor.stray_key_map = {None: {'federatedID,testuser2000@example.com,': set()}}
        rule_processor.options["max_adobe_only_users"] = "20%"
        rule_processor.process_strays({})
        stream.flush()
        actual_logger_output = stream.getvalue()
        assert "Processing Adobe-only users..." in actual_logger_output

def test_is_selected_user_key(rule_processor):
    compiled_expression = re.compile(r'\A' + "nuver.yusser@seaofcarag.com" + r'\Z', re.IGNORECASE)
    rule_processor.options['username_filter_regex'] = compiled_expression
    result = rule_processor.is_selected_user_key('federatedID,nuver.yusser@seaofcarag.com,')
    assert result
    result = rule_processor.is_selected_user_key('federatedID,test@test.com,')
    assert not result
    compiled_expression = re.compile(r'\A' + ".*sser@seaofcarag.com" + r'\Z', re.IGNORECASE)
    rule_processor.options['username_filter_regex'] = compiled_expression
    result = rule_processor.is_selected_user_key('federatedID,nuver.yusser@seaofcarag.com,')
    assert result

