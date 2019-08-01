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

import sys

from setuptools import setup

version_namespace = {}
with open('user_sync/version.py') as f:
    exec(f.read(), version_namespace)

setup(name='user-sync-sign-sync',
      version=version_namespace['__version__'],
      description='Application for synchronizing customer directories with the Adobe Enterprise Admin Console w/ Sign Features',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
      ],
      url='https://github.com/NathanNguyen345/user-sync.py',
      maintainer='Nathan Nguyen',
      maintainer_email='nnguyen@adobe.com',
      license='MIT',
      packages=['user_sync', 'user_sync.connector', 'user_sync.sign_sync', 'user_sync.sign_sync.connections'],
      install_requires=[
          'keyring',
          'okta',
          'psutil',
          'pycryptodome',
          'pyldap==2.4.45',
          'PyYAML',
          'six',
          'umapi-client>=2.10',
      ],
      extras_require={
          ':sys_platform=="linux" or sys_platform=="linux2"':[
              'secretstorage',
              'dbus-python'
          ],
          ':sys_platform=="win32"':[
              'pywin32-ctypes'
          ]
      },
      setup_requires=['nose>=1.0'],
      tests_require=[
          'mock',
          'nose>=1.0',
      ],
      entry_points={
          'console_scripts': [
              'user_sync = user_sync.app:main'
          ]
      },
      zip_safe=False)
