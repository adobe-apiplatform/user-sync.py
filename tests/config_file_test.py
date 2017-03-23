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
import yaml

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
        self.assertEqual(expected, result, error_message + '\nexpected: %s, got: %s' % (expected, result))

    def assert_dict_eq(self, exp, res, err_msg):
        '''
        compares the result dict against the expected dict, and recursively
        asserts that their content matches. The error message is given if an
        error was encountered, and the expected and actual results are given
        as well.
        '''
        def assert_sub_value_eq(exp_val, res_val):
            if isinstance(exp_val, dict):
                assert_sub_dict_eq(exp_val, res_val)
            elif isinstance(exp_val, list):
                assert_sub_list_eq(exp_val, res_val)
            else:
                self.assertEqual(exp_val, res_val)
        
        def assert_sub_list_eq(exp, res):
            '''
            compares the result list against the expected list recursively, and
            raises an assertion error if ti's values or sub-values don't match
            '''
            self.assertIsInstance(exp, list, 'expected is not dict')
            self.assertIsInstance(res, list, 'result is not list')
            
            self.assertEqual(len(exp), len(res), 'expected and result lists don\'t have the same number of entries')
            
            for exp_item, res_item in zip(exp, res):
                assert_sub_value_eq(exp_item, res_item)
    
        def assert_sub_dict_eq(exp, res):
            '''
            compares the result dict against the expected dict recursively, and
            raises an assertion error if it's values or sub-values don't match.
            '''
            self.assertIsInstance(exp, dict, 'expected is not dict')
            self.assertIsInstance(res, dict, 'result is not dict')
            
            self.assertEqual(len(exp.keys()), len(res.keys()), 'expected and result dicts don\'t have the same number of keys')
    
            for key in exp.keys():
                assert_sub_value_eq(exp[key], res[key])
            
        try:
            assert_sub_dict_eq(exp, res)
        except AssertionError as e:
            raise AssertionError('%s\n%s' % (err_msg, e.message))
        
    def test_load_root_config(self):
        '''
        tests ConfigFileLoader.load_root_config by inputing a root configuration
        file from the specified test file path, and asserts that the resulting
        processed content has the file references properly updated by comparing
        it against an expected results file, localized to the test platform
        '''
        yml = ConfigFileLoader.load_root_config('tests/test_files/root_config.yml')

        # load expected result
        with open('tests/test_files/root_config_expected.yml', 'r', 1) as input_file:
            exp_yml = yaml.load(input_file)
        
        # update paths in expected results to absoluate paths on this platform
        exp_yml['dashboard']['owning'] = os.path.abspath(exp_yml['dashboard']['owning']);
        exp_yml['dashboard']['accessors']['test-org-1']['enterprise']['priv_key_path'] = os.path.abspath(exp_yml['dashboard']['accessors']['test-org-1']['enterprise']['priv_key_path']);
        exp_yml['dashboard']['accessors']['test-org-2'] = os.path.abspath(exp_yml['dashboard']['accessors']['test-org-2']);
        exp_yml['dashboard']['accessor_config_filename_format'] = os.path.abspath(exp_yml['dashboard']['accessor_config_filename_format']);
        exp_yml['logging']['file_log_directory'] = os.path.abspath(exp_yml['logging']['file_log_directory']);

        self.assert_dict_eq(yml, exp_yml, 'test root configuration did not match expected configuration')

    def test_load_root_default_config(self):
        '''
        tests ConfigFileLoader.load_root_config by inputing a root configuration
        file path, and asserts that the resulting processed content has the
        file references properly updated
        '''
        yml = ConfigFileLoader.load_root_config('tests/test_files/root_default_config.yml')

        # load expected result
        with open('tests/test_files/root_default_config_expected.yml', 'r', 1) as input_file:
            exp_yml = yaml.load(input_file)
        
        # update paths in expected results to absoluate paths on this platform
        exp_yml['dashboard']['owning'] = os.path.abspath(exp_yml['dashboard']['owning']);
        exp_yml['dashboard']['accessor_config_filename_format'] = os.path.abspath(exp_yml['dashboard']['accessor_config_filename_format']);
        exp_yml['logging']['file_log_directory'] = os.path.abspath(exp_yml['logging']['file_log_directory']);

        self.assert_dict_eq(yml, exp_yml, 'test root default configuration did not match expected configuration')

    def test_load_sub_config(self):
        '''
        same purpose as test_load_root_config, but tests against sub
        configuration path updates (which is currently only the private key
        path in the dashboard configuration file)
        '''
        yml = ConfigFileLoader.load_sub_config('tests/test_files/sub_config.yml')

        # load expected result
        with open('tests/test_files/sub_config_expected.yml', 'r', 1) as input_file:
            exp_yml = yaml.load(input_file)
        
        # update paths in expected results to absoluate paths on this platform
        exp_yml['enterprise']['priv_key_path'] = os.path.abspath(exp_yml['enterprise']['priv_key_path']);

        self.assert_dict_eq(yml, exp_yml, 'test sub configuration did not match expected configuration')
 