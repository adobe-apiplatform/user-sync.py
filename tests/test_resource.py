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
import sys
import pytest
from user_sync import resource


@pytest.fixture
def resource_file():
    """
    Create an empty resource file
    :return:
    """
    def _resource_file(dirname, filename):
        filepath = os.path.join(dirname, filename)
        open(filepath, 'a').close()
        return filepath
    return _resource_file


def test_nonexe_root_path():
    """Test find_resource_root when not executing in EXE"""
    test_path = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', resource._DIR))
    assert test_path == resource.find_resource_root()


def test_exe_root_path(tmpdir):
    """Test find_resource_root when executing in PyInstaller EXE"""
    setattr(sys, 'frozen', True)
    setattr(sys, '_MEIPASS', tmpdir)
    test_path = os.path.join(sys._MEIPASS, resource._DIR)
    os.mkdir(test_path)
    assert test_path == resource.find_resource_root()
    delattr(sys, 'frozen')
    delattr(sys, '_MEIPASS')


def test_exe_root_path_no_dir():
    """No runtime root directory defined when running from EXE"""
    setattr(sys, 'frozen', True)
    with pytest.raises(AttributeError):
        resource.find_resource_root()
    delattr(sys, 'frozen')


def test_root_path_invalid_dir():
    """Assert that resource root dir is valid"""
    setattr(sys, 'frozen', True)
    setattr(sys, '_MEIPASS', "/fake/path")
    with pytest.raises(AssertionError):
        resource.find_resource_root()
    delattr(sys, 'frozen')
    delattr(sys, '_MEIPASS')


def test_resource_file(resource_file, tmpdir):
    """test for valid resource file"""
    setattr(sys, 'frozen', True)
    setattr(sys, '_MEIPASS', tmpdir)
    rootdir = os.path.join(sys._MEIPASS, resource._DIR)
    os.mkdir(rootdir)

    resfile = "test.txt"
    assert resource_file(rootdir, resfile) == resource.get_resource(resfile)
    delattr(sys, 'frozen')
    delattr(sys, '_MEIPASS')
    setattr(resource, '_resource_root', None)


def test_resource_invalid_file(tmpdir):
    """test for non-existent resource file"""
    setattr(sys, 'frozen', True)
    setattr(sys, '_MEIPASS', tmpdir)
    rootdir = os.path.join(sys._MEIPASS, resource._DIR)
    os.mkdir(rootdir)

    resfile = "test.txt"
    assert resource.get_resource(resfile) is None
    delattr(sys, 'frozen')
    delattr(sys, '_MEIPASS')
    setattr(resource, '_resource_root', None)


def test_resource_dir(resource_file, tmpdir):
    """test for valid resource files in directory"""
    setattr(sys, 'frozen', True)
    setattr(sys, '_MEIPASS', tmpdir)
    rootdir = os.path.join(sys._MEIPASS, resource._DIR)
    os.mkdir(rootdir)

    test_dir = os.path.join(rootdir, "test")
    os.mkdir(test_dir)

    resfile = "test_{}.txt"

    res_paths = [resource_file(test_dir, resfile.format(n+1)) for n in range(3)]

    assert res_paths == resource.get_resource_dir('test')

    delattr(sys, 'frozen')
    delattr(sys, '_MEIPASS')
    setattr(resource, '_resource_root', None)


def test_resource_dir_empty(tmpdir):
    """test for empty resource directory"""
    setattr(sys, 'frozen', True)
    setattr(sys, '_MEIPASS', tmpdir)
    rootdir = os.path.join(sys._MEIPASS, resource._DIR)
    os.mkdir(rootdir)

    test_dir = os.path.join(rootdir, "test")
    os.mkdir(test_dir)

    assert [] == resource.get_resource_dir('test')

    delattr(sys, 'frozen')
    delattr(sys, '_MEIPASS')
    setattr(resource, '_resource_root', None)


def test_resource_dir_invalid(tmpdir):
    """test for nonexistent resource directory"""
    setattr(sys, 'frozen', True)
    setattr(sys, '_MEIPASS', tmpdir)
    rootdir = os.path.join(sys._MEIPASS, resource._DIR)
    os.mkdir(rootdir)

    with pytest.raises(AssertionError):
        resource.get_resource_dir('test')

    delattr(sys, 'frozen')
    delattr(sys, '_MEIPASS')
    setattr(resource, '_resource_root', None)
