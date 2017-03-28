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

import unittest
import tests.helper
from user_sync.config import ConfigFileLoader

class ConfigFileLoaderTest(unittest.TestCase):
    def test_load_root_config(self):
        '''
        tests ConfigFileLoader.load_root_config by inputing various root
        configuration file paths, and asserts that the resulting processed
        content has the file references properly updated by comparing it against
        an expected results file, converted to a path form native to the
        platform
        '''
        tests.helper.assert_configs(self, [
            { 'result':ConfigFileLoader.load_root_config('tests/test_files/root_config/normal/config.yml'), 'expected':'tests/test_files/root_config/normal/expected.yml' },
            { 'result':ConfigFileLoader.load_root_config('tests/test_files/root_config/default_settings/config.yml'), 'expected':'tests/test_files/root_config/default_settings/expected.yml' }
        ])

    def test_load_sub_config(self):
        '''
        same purpose as test_load_root_config, but tests against sub
        configuration path updates (which is currently only the private key
        path in the dashboard configuration file)
        '''
        tests.helper.assert_configs(self, [
            { 'result':ConfigFileLoader.load_sub_config('tests/test_files/sub_config/normal/config.yml'), 'expected':'tests/test_files/sub_config/normal/expected.yml' }
        ])
