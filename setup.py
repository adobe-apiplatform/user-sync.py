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

from setuptools import setup, find_packages

version_namespace = {}
with open('user_sync/version.py') as f:
    exec(f.read(), version_namespace)

test_deps = ['mock', 'pytest', 'pytest-cov']
setup_deps = ['pytest-runner']

setup(name='user-sync',
      version=version_namespace['__version__'],
      description='Application for synchronizing customer directories with the Adobe Enterprise Admin Console',
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
      url='https://github.com/adobe-apiplatform/user-sync.py',
      maintainer='Daniel Brotsky',
      maintainer_email='dbrotsky@adobe.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'keyring',
          'okta==0.0.3.1',
          'psutil',
          'pycryptodome==3.7.3',
          'ldap3==2.6.1',
          'PyYAML',
          'six',
          'umapi-client>=2.12',
          'click',
          'click-default-group',
      ],
      extras_require={
          ':python_version<"3"':[
              'zipp==1.1.0',
          ],
          ':sys_platform=="linux" or sys_platform=="linux2"': [
              'secretstorage',
              'dbus-python',
          ],
          ':sys_platform=="win32"': [
              'pywin32-ctypes'
          ],
          'test': test_deps,
          'setup': setup_deps,
      },
      setup_requires=setup_deps,
      tests_require=test_deps,
      entry_points={
          'console_scripts': [
              'user_sync = user_sync.app:main'
          ]
      },
      package_data={'user_sync.resources': ['*', 'examples/*']},
      zip_safe=False)
