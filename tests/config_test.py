import unittest

import mock


import aedash
import tests.helper
from aedash.sync.config import ConfigLoader


class ConfigLoaderTest(unittest.TestCase):
    @mock.patch('os.path.isfile')
    @mock.patch('aedash.sync.config.DictConfig.get_value')
    @mock.patch('aedash.sync.config.ConfigLoader.load_from_yaml')
    @mock.patch('aedash.sync.config.ConfigLoader.get_dict_from_sources')
    def test_get_dashboard_options_for_owning(self,mock_get_dict,mock_yaml_load,mock_get_value,mock_isfile,):

        conf_load = ConfigLoader({})


        mock_isfile.return_value = True
        conf_load.get_dashboard_options_for_owning()

        mock_isfile.return_value = False
        conf_load.get_dashboard_options_for_owning()
        self.assertRaises(aedash.sync.error.AssertionException,)

        # def get_dashboard_options_for_owning(self):
        #     owning_config_filename = DEFAULT_DASHBOARD_OWNING_CONFIG_FILENAME
        #
        #     owning_config = None
        #     dashboard_config = self.main_config.get_dict_config('dashboard', True)
        #     if (dashboard_config != None):
        #         owning_config = dashboard_config.get_list('owning', True)
        #     owning_config_sources = self.as_list(owning_config)
        #     if (os.path.isfile(owning_config_filename)):
        #         owning_config_sources.append(owning_config_filename)
        #     owning_config_sources.append({
        #         'test_mode': self.options['test_mode']
        #     })
        #     return self.create_dashboard_options(owning_config_sources, 'owning_dashboard')
