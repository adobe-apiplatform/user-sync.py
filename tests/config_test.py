import unittest

import mock

from aedash.sync.config import ConfigLoader


class ConfigLoaderTest(unittest.TestCase):

    @mock.patch('os.path.isfile')
    @mock.patch('aedash.sync.config.ConfigLoader.load_from_yaml')
    def setUp(self,mock_yaml,mock_isfile):
        mock_isfile.return_value = True
        self.conf_load = ConfigLoader({'options':'testOpt'})


    @mock.patch('aedash.sync.config.DictConfig.get_value')
    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    @mock.patch('aedash.sync.config.ConfigLoader.create_dashboard_options')
    def test_get_dashboard_options_creates_dashboard(self,mock_create_dash, mock_dict, mock_value):
        ret_value = 'create dash'
        mock_create_dash.return_value = ret_value
        self.assertEquals(self.conf_load.get_dashboard_options_for_owning(),ret_value, 'Returned with created dashboard')
        self.assertEquals(mock_create_dash.call_count,1, 'Get dashboard options calls create dashboard options')


    @mock.patch('aedash.sync.config.ConfigLoader.get_directory_connector_configs')
    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    def test_get_directory_connector_options(self,mock_dict, mock_connector_conf):
        self.conf_load.get_directory_connector_options('dummy_connector')
        self.assertEquals(mock_dict.call_count, 3, 'connector options, source filters and credentials are loaded')


    @mock.patch('aedash.sync.config.DictConfig.get_dict_config')
    @mock.patch('aedash.sync.config.ConfigLoader.create_dashboard_options')
    @mock.patch('glob.glob1')
    @mock.patch('aedash.sync.config.ConfigLoader.parse_string')
    def test_get_dashboard_options_for_trustees(self,mock_parse,mock_glob,mock_create_dash,mock_get_dict):
        mock_create_dash.return_value = {'create_dash'}
        mock_glob.return_value = {''}
        mock_parse.return_value = {'organization_name':'testOrgName'}

        self.assertEquals(self.conf_load.get_dashboard_options_for_trustees(),{'testOrgName': set(['create_dash'])},'We return with trustee option in the expected format')
        self.assertEquals(mock_create_dash.call_count, 1, 'create dashboard options was called')


    def test_get_dict_from_sources_dict(self):
        self.assertEquals(self.conf_load.get_dict_from_sources([{'test1':'test2'},{'test1':'test3'}],'')
                          ,{'test1': 'test3'},'the two dictionaries are combined')