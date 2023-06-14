# Copyright (c) 2016-2017 Adobe Inc.  All rights reserved.
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

import os
import pytest
import configparser
from user_sync import resource
from user_sync import flags


@pytest.fixture
def flag_data_file(resource_file, tmpdir):
    """Create a temporary flag data resource file"""
    tmpdir = str(tmpdir)

    def _flag_data_file(filename, data):
        res_file = resource_file(tmpdir, filename)
        cfg = configparser.ConfigParser()
        cfg.optionxform = str
        cfg['config'] = data
        with open(res_file, 'w') as f:
            cfg.write(f)
        return res_file
    return _flag_data_file


@pytest.fixture
def default_flag_data():
    """Data for default_flags.cfg"""
    return {
        'UST_EXTENSION': '1',
    }


def patch_flag_resource(flag_file_path, default_file_path):
    """Return a closure to patch resource.get_resource()"""
    def _patch_flag_resource(res):
        if res == 'flags.cfg':
            return flag_file_path
        else:
            return default_file_path
    return _patch_flag_resource


def test_flags_cfg_init(flag_data_file, default_flag_data, monkeypatch):
    """Ensure the flag manager is using the flag data over the default_config"""
    flag_data = {
        'UST_EXTENSION': '0',
    }
    flag_file = flag_data_file('flags.cfg', flag_data)
    default_file = flag_data_file('default_flags.cfg', default_flag_data)

    with monkeypatch.context() as m:
        m.setattr(resource, 'get_resource', patch_flag_resource(flag_file, default_file))
        m.setattr(resource, '_config', {}, False)
        flags._init_config()
        assert 'UST_EXTENSION' in flags._config and not flags.get_flag('UST_EXTENSION')


def test_flags_cfg_invalid_key(flag_data_file, default_flag_data, monkeypatch):
    """Raise an exception when giving the flag manager an invalid key"""
    flag_data = {
        'UST_EXTENSION': '0',
    }
    flag_file = flag_data_file('flags.cfg', flag_data)
    default_file = flag_data_file('default_flags.cfg', default_flag_data)

    with monkeypatch.context() as m:
        m.setattr(resource, 'get_resource', patch_flag_resource(flag_file, default_file))
        m.setattr(resource, '_config', {}, False)
        flags._init_config()
        with pytest.raises(AssertionError):
            flags.get_flag('INVALID_KEY')


def test_flags_default_cfg(flag_data_file, default_flag_data, monkeypatch):
    """Use default config if flags.cfg is not present"""
    default_file = flag_data_file('default_flags.cfg', default_flag_data)

    with monkeypatch.context() as m:
        m.delenv('UST_EXTENSION', raising=False)
        m.setattr(resource, 'get_resource', patch_flag_resource(None, default_file))
        m.setattr(resource, '_config', {}, False)
        flags._init_config()
        assert 'UST_EXTENSION' in flags._config and flags.get_flag('UST_EXTENSION')


def test_flags_env_vars(flag_data_file, default_flag_data, monkeypatch):
    """Ensure that environment variables override defaults if no flags file specified"""
    default_file = flag_data_file('default_flags.cfg', default_flag_data)

    with monkeypatch.context() as m:
        m.setattr(resource, 'get_resource', patch_flag_resource(None, default_file))
        m.setattr(resource, '_config', {}, False)
        m.setenv('UST_EXTENSION', '0')
        flags._init_config()
        assert 'UST_EXTENSION' in flags._config and not flags.get_flag('UST_EXTENSION')


def test_flags_flags_and_envs(flag_data_file, default_flag_data, monkeypatch):
    """If flags file and env vars specified, ensure that flags take precedence"""
    flag_data = {
        'UST_EXTENSION': '1',
    }
    flag_file = flag_data_file('flags.cfg', flag_data)
    default_file = flag_data_file('default_flags.cfg', default_flag_data)

    with monkeypatch.context() as m:
        m.setattr(resource, 'get_resource', patch_flag_resource(flag_file, default_file))
        m.setattr(resource, '_config', {}, False)
        m.setenv('UST_EXTENSION', '0')
        flags._init_config()
        assert 'UST_EXTENSION' in flags._config and flags.get_flag('UST_EXTENSION')
