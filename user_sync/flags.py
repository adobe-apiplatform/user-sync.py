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
from backports import configparser
from user_sync import resource

_config = {}


def _read_config(config_file):
    """
    Read a config file and return a dict containing config data

    :param str config_file: path to config
    :return dict(str, str): config data dict
    """
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(config_file)
    return dict(cfg.items('config'))


def _init_config():
    """
    Initialize _config based on flags.cfg, environment variables and/or default_flags.cfg
    """
    global _config

    default_data = _read_config(resource.get_resource('default_flags.cfg'))
    flag_config_file = resource.get_resource('flags.cfg')
    if flag_config_file is None:
        flag_data = {}
    else:
        flag_data = _read_config(flag_config_file)

    for k, v in default_data.items():
        if k not in flag_data:
            env_val = os.environ.get(k)
            if env_val is not None:
                _config[k] = bool(int(env_val))
            else:
                _config[k] = bool(int(v))
        else:
            _config[k] = bool(int(flag_data[k]))


def get_flag(key):
    """
    Get feature flag setting
    :param str key: key of feature flag
    :return bool: bool representing flag setting (True if enabled, False if disabled)
    """
    if not _config:
        _init_config()
    flag_val = _config.get(key)
    assert flag_val is not None, "flag key '{}' does not exist".format(key)
    return flag_val
