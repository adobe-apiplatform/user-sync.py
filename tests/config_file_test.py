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
import os
import os.path
import yaml
import six

import mock
import tests.helper
import user_sync.identity_type
from user_sync.error import AssertionException
from user_sync.config import ConfigLoader
from user_sync.config import ConfigFileLoader
from user_sync.config import ObjectConfig
from mock.mock import patch

class ConfigFileLoaderTest(unittest.TestCase):
    def assert_eq(self, result, expected, error_message):
        '''
        compares the result against the expected value, and outputs an error
        message if they don't match. Also outputs the expected and result
        values.
        '''
        self.assertEqual(result, expected, error_message + '\nexpected: %s, got: %s' % (expected, result))
    
    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    @mock.patch('os.path.isfile')
    def test_load_root_config(self, mock_isfile, mock_yaml, mock_open):
        '''
        tests ConfigFileLoader.load_root_config by inputing a root configuration
        file path, and asserts that the resulting processed content has the
        file references properly updated
        :type mock_isfile: Mock
        :type mock_yaml: Mock
        :type mock_open: Mock
        '''
        mock_isfile.return_value = True
        mocked_open = mock_open('test')
        mocked_open_name = '%s.open' % __name__
        with patch(mocked_open_name, mocked_open, create=True):
            mock_yaml.return_value = {
                    'logging':{
                            'file_log_directory':'log-test-1'
                        },
                    'other':{
                            'test-string':'test string value should not change',
                            'test-dict':{
                                    'test-string-2':'this should not change as well'
                                },
                            'test-list':[
                                'item-1',
                                'item-2',
                                {
                                    'test-string-3':'xyz'
                                }
                                ]
                        }
                }
            yml = ConfigFileLoader.load_root_config('config-test/user-sync-config-test.yml')
            
            # test path updating
            self.assert_eq(yml['logging']['file_log_directory'], os.path.abspath('config-test/log-test-1'),
                           'logging path is incorrect')

            # test control keys
            self.assert_eq(yml['other']['test-string'], 'test string value should not change',
                           '/other/test-string value should not change')
            self.assert_eq(yml['other']['test-dict']['test-string-2'], 'this should not change as well',
                           '/other/test-dict/test-string-2 value should not change')
            self.assert_eq(yml['other']['test-list'][0], 'item-1',
                           '/other/test-list/[0] value should not change')
            self.assert_eq(yml['other']['test-list'][2]['test-string-3'], 'xyz',
                           '/other/test-list/[2] value should not change')

    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    @mock.patch('os.path.isfile')
    def test_load_root_default_config(self, mock_isfile, mock_yaml, mock_open):
        '''
        tests ConfigFileLoader.load_root_config by inputing a root configuration
        file path, and asserts that the resulting processed content has the
        file references properly updated
        :type mock_isfile: Mock
        :type mock_yaml: Mock
        :type mock_open: Mock
        '''
        mock_isfile.return_value = True
        mocked_open = mock_open('test')
        mocked_open_name = '%s.open' % __name__
        with patch(mocked_open_name, mocked_open, create=True):
            mock_yaml.return_value = {
                    'adobe_users': {'connectors': {'umapi': 'test-123'}},
                    'logging': {'log_to_file': True},
                }
            yml = ConfigFileLoader.load_root_config('config-test-2/user-sync-config-test.yml')

            # assert default values are preserved
            self.assert_eq(yml['logging']['file_log_directory'], os.path.abspath('config-test-2/logs'),
                           'default log path is missing or incorrect')

            # assert file paths are still updated properly
            self.assert_eq(yml['adobe_users']['connectors']['umapi'], os.path.abspath('config-test-2/test-123'),
                           'default primary umapi configuration path is incorrect')

    @mock.patch('builtins.open')
    @mock.patch('yaml.load')
    @mock.patch('os.path.isfile')
    def test_load_sub_config(self, mock_isfile, mock_yaml, mock_open):
        '''
        same purpose as test_load_root_config, but tests against sub
        configuration path updates (which is currently only the private key
        path in the umapi configuration file)
        :type mock_isfile: Mock
        :type mock_yaml: Mock
        :type mock_open: Mock
        '''
        mock_isfile.return_value = True
        mocked_open = mock_open('test')
        mocked_open_name = '%s.open' % __name__
        with patch(mocked_open_name, mocked_open, create=True):
            mock_yaml.return_value = {
                    'enterprise':{
                            'priv_key_path':'../keys/test-key.key',
                            'test':'value should not change'
                        },
                    'other': {
                            'test-2': 123
                        }
                }
            yml = ConfigFileLoader.load_sub_config('sub-config-test/user-sync-config-test.yml')
            
            # test path updating
            self.assert_eq(yml['enterprise']['priv_key_path'], os.path.abspath('keys/test-key.key'),
                           'private key path is incorrect')

            # test control keys
            self.assert_eq(yml['enterprise']['test'], 'value should not change',
                           '/enterprise/test value should not change')
            self.assert_eq(yml['other']['test-2'], 123, '/other/test-2 value should not change')
