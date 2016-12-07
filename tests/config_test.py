import unittest

import mock


import aedash
import tests.helper
from aedash.sync.config import ConfigLoader


class ConfigLoaderTest(unittest.TestCase):

    @mock.patch('os.path.isfile')
    @mock.patch('aedash.sync.config.ConfigLoader.load_from_yaml')
    def setUp(self,mock_yaml,mock_isfile):
        mock_isfile.return_value = True
        self.conf_load = ConfigLoader({})


    @mock.patch('aedash.sync.config.DictConfig.get_value')
    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    @mock.patch('aedash.sync.config.ConfigLoader.create_dashboard_options')
    def test_get_dashboard_options_creates_dashboard(self,mock_create_dash, mock_dict, mock_value):
        ret_value = 'create dash'
        mock_create_dash.return_value = ret_value
        self.assertEquals(self.conf_load.get_dashboard_options_for_owning(),ret_value, "Returned with created dashboard")
        self.assertEquals(mock_create_dash.call_count,1, "Get dashboard options calls create dashboard options")


    @mock.patch('aedash.sync.config.ConfigLoader.get_directory_connector_configs')
    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    def test_get_directory_connector_options(self,mock_dict, mock_connector_conf):
        self.assertEquals(mock_dict.call_count, 3, "connector options, source filters and credentials are loaded")


    if __name__ == "__main__":
        unittest.main()