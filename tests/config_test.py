# Copyright (c) 2016-2017 Adobe Systems Incorporated.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import types
import unittest

import mock
import tests.helper
from user_sync.error import AssertionException
from user_sync.config import ConfigLoader
from user_sync.config import ObjectConfig


class ConfigLoaderTest(unittest.TestCase):
    @mock.patch('os.path.isfile')
    @mock.patch('user_sync.config.ConfigLoader.load_from_yaml')
    def setUp(self, mock_yaml, mock_isfile):
        mock_isfile.return_value = True
        self.conf_load = ConfigLoader({'options': 'testOpt'})

    @mock.patch('user_sync.config.DictConfig.get_value')
    @mock.patch('user_sync.config.ConfigLoader.get_dict_from_sources')
    @mock.patch('user_sync.config.ConfigLoader.create_dashboard_options')
    def test_get_dashboard_options_creates_dashboard(self, mock_create_dash, mock_dict, mock_value):
        ret_value = 'create dash'
        mock_create_dash.return_value = ret_value
        self.assertEquals(self.conf_load.get_dashboard_options_for_owning(), ret_value,
                          'Returned with created dashboard')
        self.assertEquals(mock_create_dash.call_count, 1, 'Get dashboard options calls create dashboard options')

    @mock.patch('user_sync.config.ConfigLoader.get_directory_connector_configs')
    @mock.patch('user_sync.config.ConfigLoader.get_dict_from_sources')
    def test_get_directory_connector_options(self, mock_dict, mock_connector_conf):
        self.conf_load.get_directory_connector_options('dummy_connector')
        self.assertEquals(mock_dict.call_count, 3, 'connector options, source filters and credentials are loaded')

    @mock.patch('user_sync.config.DictConfig.get_dict_config')
    @mock.patch('user_sync.config.ConfigLoader.create_dashboard_options')
    @mock.patch('glob.glob1')
    @mock.patch('user_sync.config.ConfigLoader.parse_string')
    def test_get_dashboard_options_for_accessors(self, mock_parse, mock_glob, mock_create_dash, mock_get_dict):
        mock_create_dash.return_value = {'create_dash'}
        mock_glob.return_value = {''}
        mock_parse.return_value = {'organization_name': 'testOrgName'}

        self.assertEquals(self.conf_load.get_dashboard_options_for_accessors(), {'testOrgName': set(['create_dash'])},
                          'We return with accessor option in the expected format')
        self.assertEquals(mock_create_dash.call_count, 1, 'create dashboard options was called')

    def test_get_dict_from_sources_dict(self):
        self.assertEquals(self.conf_load.get_dict_from_sources([{'test1': 'test2'}, {'test1': 'test3'}], ''),
                          {'test1': 'test3'}, 'the two dictionaries are combined')

    @mock.patch('os.path.isfile')
    def test_get_dict_from_sources_str_not_found(self, mock_isfile):
        # AssertionException when file is not found
        mock_isfile.return_value = False
        self.assertRaises(AssertionException, lambda: self.conf_load.get_dict_from_sources(['test'], ''))

    @mock.patch('os.path.isfile')
    def test_get_dict_from_sources_str_found(self, mock_isfile):
        # IOError when file is found, but not loaded by load_from_yaml
        mock_isfile.return_value = True
        self.assertRaises(IOError, lambda: self.conf_load.get_dict_from_sources(['test'], ''))

    @mock.patch('user_sync.config.ConfigLoader.get_dict_from_sources')
    def test_create_dashboard_options(self, mock_dict):
        mock_dict.side_effect = [{'enterprise': {'org_id': 'test1'}}, 'test2']
        self.assertEquals(self.conf_load.create_dashboard_options('', ''), {'enterprise': 'test2'},
                          'enterprise section is processed')

    @mock.patch('user_sync.config.DictConfig.get_string')
    @mock.patch('user_sync.config.DictConfig.get_dict_config')
    @mock.patch('user_sync.identity_type.parse_identity_type')
    def test_get_rule_options(self, mock_id_type,mock_get_dict,mock_get_string):
        mock_id_type.return_value = 'new_acc'
        mock_get_dict.return_value = tests.helper.MockGetString()
        self.assertEquals(self.conf_load.get_rule_options(), {'username_filter_regex': None,
                                                              'update_user_info': True,
                                                              'manage_groups': True,
                                                              'new_account_type': 'new_acc',
                                                              'directory_group_filter': None,
                                                              'default_country_code': 'test',
                                                              'remove_user_key_list': None,
                                                              'remove_list_output_path': None,
                                                              'remove_nonexistent_users': False},
                          'rule options are returned')

    def test_parse_string(self):
        self.assertEquals(self.conf_load.parse_string('{1}{2}{3}', 'abcde'),
                          {'1': 'abc', '3': 'e', '2': 'd'}, 'test parsing 1')
        self.assertEquals(self.conf_load.parse_string('{1}', 'abcde'),{'1': 'abcde'}, 'test parsing 2')

    @mock.patch('user_sync.config.ConfigLoader.get_directory_connector_configs')
    def test_check_unused_config_keys_unused(self,mock_connector_conf):
        self.conf_load.options = {'directory_source_filters': {'filter':'test1'}}
        self.conf_load.directory_source_filters_accessed = set({'another_filter':'test2'})
        # Assertion Exception is raised for unused keys
        self.assertRaises(AssertionException,lambda : self.conf_load.check_unused_config_keys())

    @mock.patch('user_sync.config.ConfigLoader.get_directory_connector_configs')
    def test_check_unused_config_keys_used(self,mock_connector_conf):
        self.conf_load.options = {'directory_source_filters': {'filter':'test1'}}
        self.conf_load.directory_source_filters_accessed = set({'filter':'test2'})

        self.assertEquals(self.conf_load.check_unused_config_keys(),None,'no unused keys')


class ObjectConfigTest(unittest.TestCase):
    def setUp(self):
        self.object_conf = ObjectConfig(self)

    def test_describe_types(self):
        self.assertEquals(self.object_conf.describe_types(types.StringTypes), ['str'], 'strings are handeled')
        self.assertEquals(self.object_conf.describe_types(types.BooleanType), ['bool'], 'other types are handeled')
