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
import pkg_resources
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


def test_resource_file_bundle(resource_file, tmpdir, monkeypatch):
    """test for valid resource file in an EXE bundle"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        m.setattr(resource, '_run_context', None, False)
        m.setattr(sys, 'frozen', True, False)
        m.setattr(sys, '_MEIPASS', tmpdir, False)
        rootdir = os.path.join(sys._MEIPASS, resource._BUNDLE_DIR)
        os.mkdir(rootdir)

        resfile = "test.txt"
        assert resource_file(rootdir, resfile) == resource.get_resource(resfile)


def test_resource_file_package(resource_file, tmpdir, monkeypatch):
    """test for valid resource file in a Package context"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        resfile = "test.txt"
        m.setattr(pkg_resources, "resource_filename", lambda *args: os.path.join(tmpdir, resfile))
        assert resource_file(tmpdir, resfile) == resource.get_resource(resfile)


def test_resource_invalid_file_bundle(tmpdir, monkeypatch):
    """test for non-existent resource file in a bundle"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        m.setattr(resource, '_run_context', None, False)
        m.setattr(sys, 'frozen', True, False)
        m.setattr(sys, '_MEIPASS', tmpdir, False)

        rootdir = os.path.join(sys._MEIPASS, resource._BUNDLE_DIR)
        os.mkdir(rootdir)

        resfile = "test.txt"
        assert resource.get_resource(resfile) is None


def test_resource_invalid_file_package(tmpdir, monkeypatch):
    """test for non-existent resource file in a package"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        m.setattr(pkg_resources, "resource_filename", lambda *args: os.path.join('invalid', 'file', 'path'))
        resfile = os.path.join('invalid', 'file', 'path')
        assert resource.get_resource(resfile) is None


def test_resource_dir_bundle(resource_file, tmpdir, monkeypatch):
    """test for valid resource files in directory in standalone run context"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        m.setattr(resource, '_run_context', None, False)
        m.setattr(sys, 'frozen', True, False)
        m.setattr(sys, '_MEIPASS', tmpdir, False)

        rootdir = os.path.join(sys._MEIPASS, resource._BUNDLE_DIR)
        os.mkdir(rootdir)

        test_dir = os.path.join(rootdir, "test")
        os.mkdir(test_dir)

        resfile = "test_{}.txt"

        res_paths = [resource_file(test_dir, resfile.format(n+1)) for n in range(3)]

        assert sorted(res_paths) == sorted(resource.get_resource_dir('test'))


def test_resource_dir_package(resource_file, tmpdir, monkeypatch):
    """test for valid resource files in directory in package run context"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        test_dir = os.path.join(tmpdir, "test")
        os.mkdir(test_dir)

        m.setattr(pkg_resources, "resource_filename", lambda *args: os.path.join(tmpdir, test_dir))

        resfile = "test_{}.txt"

        res_test_files = [resfile.format(n+1) for n in range(3)]

        m.setattr(pkg_resources, "resource_listdir", lambda *args: res_test_files)

        res_paths = [resource_file(test_dir, resfile.format(n+1)) for n in range(3)]

        assert sorted(res_paths) == sorted(resource.get_resource_dir('test'))


def test_resource_dir_empty(tmpdir, monkeypatch):
    """test for empty resource directory"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        m.setattr(resource, '_run_context', None, False)
        m.setattr(sys, 'frozen', True, False)
        m.setattr(sys, '_MEIPASS', tmpdir, False)

        rootdir = os.path.join(sys._MEIPASS, resource._BUNDLE_DIR)
        os.mkdir(rootdir)

        test_dir = os.path.join(rootdir, "test")
        os.mkdir(test_dir)

        assert [] == resource.get_resource_dir('test')


def test_resource_dir_invalid(tmpdir, monkeypatch):
    """test for nonexistent resource directory"""
    tmpdir = str(tmpdir)
    with monkeypatch.context() as m:
        m.setattr(resource, '_run_context', None, False)
        m.setattr(sys, 'frozen', True, False)
        m.setattr(sys, '_MEIPASS', tmpdir, False)
        rootdir = os.path.join(sys._MEIPASS, resource._BUNDLE_DIR)
        os.mkdir(rootdir)

        with pytest.raises(AssertionError):
            resource.get_resource_dir('test')
