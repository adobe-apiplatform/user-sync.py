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
import shutil
import json
import pkg_resources
from pathlib import Path
import configparser


def cd():
    os.chdir(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))


def bundle_example_config(subdir):
    examples_dir = os.path.join('examples', subdir)
    files = [os.path.join(examples_dir, f) for f in os.listdir(examples_dir) if
             os.path.isfile(os.path.join(examples_dir, f))]
    bundle_dir = os.path.join('user_sync', 'resources', 'examples')
    if not os.path.exists(bundle_dir):
        os.mkdir(bundle_dir)
    for f in files:
        dest = os.path.join(bundle_dir, os.path.split(f)[-1])
        shutil.copy(f, dest)


def bundle_feature_flag_config():
    default_cfg_path = os.path.join('user_sync', 'resources', 'default_flags.cfg')
    default_cfg = configparser.ConfigParser()
    default_cfg.optionxform = str
    default_cfg.read(default_cfg_path)

    flag_data = {}

    for k, v in default_cfg.items('config'):
        env_val = os.environ.get(k)
        if env_val is not None:
            flag_data[k] = env_val
        else:
            flag_data[k] = v

    with open(os.path.join('user_sync', 'resources', 'flags.cfg'), 'w') as flag_cfg_file:
        flag_cfg = configparser.ConfigParser()
        flag_cfg.optionxform = str
        flag_cfg['config'] = flag_data
        flag_cfg.write(flag_cfg_file)


def pkg_meta():
    pkg_meta_path = Path('user_sync', 'resources', 'pkg_meta.json')
    with open(pkg_meta_path, 'w') as f:
        json.dump({p.project_name: p.version for p in pkg_resources.working_set}, f)


if __name__ == '__main__':
    cd()
    bundle_example_config('config files - basic')
    bundle_example_config('sign')
    pkg_meta()
