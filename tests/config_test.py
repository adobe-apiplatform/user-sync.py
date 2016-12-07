import types
import unittest

import mock

from aedash.sync.error import AssertionException
from aedash.sync.config import ConfigLoader
from aedash.sync.config import ObjectConfig


class ConfigLoaderTest(unittest.TestCase):
    @mock.patch('os.path.isfile')
    @mock.patch('aedash.sync.config.ConfigLoader.load_from_yaml')
    def setUp(self, mock_yaml, mock_isfile):
        mock_isfile.return_value = True
        self.conf_load = ConfigLoader({'options': 'testOpt'})
        self.object_conf = ObjectConfig(self)

    @mock.patch('aedash.sync.config.DictConfig.get_value')
    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    @mock.patch('aedash.sync.config.ConfigLoader.create_dashboard_options')
    def test_get_dashboard_options_creates_dashboard(self, mock_create_dash, mock_dict, mock_value):
        ret_value = 'create dash'
        mock_create_dash.return_value = ret_value
        self.assertEquals(self.conf_load.get_dashboard_options_for_owning(), ret_value,
                          'Returned with created dashboard')
        self.assertEquals(mock_create_dash.call_count, 1, 'Get dashboard options calls create dashboard options')

    @mock.patch('aedash.sync.config.ConfigLoader.get_directory_connector_configs')
    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    def test_get_directory_connector_options(self, mock_dict, mock_connector_conf):
        self.conf_load.get_directory_connector_options('dummy_connector')
        self.assertEquals(mock_dict.call_count, 3, 'connector options, source filters and credentials are loaded')

    @mock.patch('aedash.sync.config.DictConfig.get_dict_config')
    @mock.patch('aedash.sync.config.ConfigLoader.create_dashboard_options')
    @mock.patch('glob.glob1')
    @mock.patch('aedash.sync.config.ConfigLoader.parse_string')
    def test_get_dashboard_options_for_trustees(self, mock_parse, mock_glob, mock_create_dash, mock_get_dict):
        mock_create_dash.return_value = {'create_dash'}
        mock_glob.return_value = {''}
        mock_parse.return_value = {'organization_name': 'testOrgName'}

        self.assertEquals(self.conf_load.get_dashboard_options_for_trustees(), {'testOrgName': set(['create_dash'])},
                          'We return with trustee option in the expected format')
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

    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    def test_create_dashboard_options(self, mock_dict):
        mock_dict.side_effect = [{'enterprise': {'org_id': 'test1'}}, 'test2']
        self.assertEquals(self.conf_load.create_dashboard_options('', ''), {'enterprise': 'test2'},
                          'enterprise section is processed')

    def test_describe_types(self):
        self.assertEquals(self.object_conf.describe_types(types.StringTypes),['str'],'strings are handeled')
        self.assertEquals(self.object_conf.describe_types(types.BooleanType),['bool'],'other types are handeled')
