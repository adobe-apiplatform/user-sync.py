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
import enum
import pkg_resources

_BUNDLE_DIR = "resources"

_PKG = "user_sync.resources"

_run_context = None


class RunContext(enum.Enum):
    EXEBundle = 'exe'
    Package = 'package'


def get_run_context():
    if getattr(sys, 'frozen', False):
        return RunContext.EXEBundle
    return RunContext.Package


def get_resource(resource):
    """
    Get a path to a single resource file
    :param str resource: Relative resource file path (relative to resource root directory)
    :return str: Absolute path to resource file or None if no resource was found
    """
    global _run_context
    if _run_context is None:
        _run_context = get_run_context()

    if _run_context == RunContext.EXEBundle:
        assert getattr(sys, '_MEIPASS', False), "Bundle root dir is not set"
        resource_path = os.path.join(getattr(sys, '_MEIPASS'), "resources", resource)
    else:
        resource_path = pkg_resources.resource_filename(_PKG, resource)
    if os.path.exists(resource_path) and os.path.isfile(resource_path):
        return resource_path
    return None


def get_resource_dir(resource_dir):
    """
    Get list of paths to all resource files for given directory.

    Only files directly contained in directory will be returned.  Recursion is not currently supported.
    :param str resource_dir: Relative path of directory (relative to resource root directory)
    :return list(str): List of resource files in directory or None if directory was not found
    """
    global _run_context
    if _run_context is None:
        _run_context = get_run_context()

    if _run_context == RunContext.EXEBundle:
        assert getattr(sys, '_MEIPASS', False)
        resource_path = os.path.join(getattr(sys, '_MEIPASS'), "resources", resource_dir)
        assert os.path.isdir(resource_path), "Resource directory does not exist"

        return [os.path.join(resource_path, f) for f in os.listdir(resource_path)
                if os.path.isfile(os.path.join(resource_path, f))]
    else:
        resource_path = pkg_resources.resource_filename(_PKG, resource_dir)
        return [os.path.join(resource_path, f) for f in pkg_resources.resource_listdir(_PKG, resource_dir)
                if os.path.isfile(os.path.join(resource_path, f))]
