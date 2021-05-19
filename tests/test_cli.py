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


from click.testing import CliRunner
from user_sync.app import example_config
import sys
import shutil
from pathlib import Path
from user_sync import resource

def test_example_config_line_endings(tmpdir, monkeypatch, test_resources):
    # Set up temp directories
    res_path = tmpdir / 'resource'
    res_path.mkdir()
    example_path = tmpdir / 'examples'
    example_path.mkdir()

    # Copy temp example config to temp resource dir
    root_tmp_file = test_resources['root_config']
    ldap_tmp_file = test_resources['ldap']
    umapi_tmp_file = test_resources['umapi']

    shutil.copyfile(ldap_tmp_file, res_path / Path(ldap_tmp_file).parts[-1])
    shutil.copyfile(root_tmp_file, res_path / Path(root_tmp_file).parts[-1])
    shutil.copyfile(umapi_tmp_file, res_path / Path(umapi_tmp_file).parts[-1])

    # patch resource.get_resource()
    def resource_patch(res):
        if 'ldap' in res:
            return str(res_path / Path(ldap_tmp_file).parts[-1])
        if 'user-sync' in res:
            return str(res_path / Path(root_tmp_file).parts[-1])
        if 'umapi' in res:
            return str(res_path / Path(umapi_tmp_file).parts[-1])
        return ''

    with monkeypatch.context() as m:
        m.setattr(resource, "get_resource", resource_patch)

        runner = CliRunner()
        example_ldap_file = example_path / Path(ldap_tmp_file).parts[-1]
        example_ust_file = example_path / Path(root_tmp_file).parts[-1]
        example_umapi_file = example_path / Path(umapi_tmp_file).parts[-1]
        runner.invoke(example_config, ['--ldap={}'.format(example_ldap_file), '--root={}'.format(example_ust_file),
                                       '--umapi={}'.format(example_umapi_file)])

        with open(example_ldap_file, 'rb') as f:
            content = f.read()
        if sys.platform == 'win32':
            assert b'\r\n' in content
        else:
            assert b'\n' in content
            assert b'\r' not in content
