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

import user_sync.error


class DirectoryConnector(object):
    def __init__(self, implementation):
        self.implementation = implementation

        required_functions = ['connector_metadata', 'connector_initialize']
        for required_function in required_functions:
            if not hasattr(implementation, required_function):
                raise user_sync.error.AssertionException('Missing function: %s source: %s' %
                                                         (required_function, implementation.__file__))

        self.metadata = metadata = implementation.connector_metadata()
        self.name = name = metadata.get('name')
        if not name:
            raise user_sync.error.AssertionException('Missing metadata property: %s source: %s' %
                                                     ('name', implementation.__file__))

    def initialize(self, options=None):
        """
        :type options: dict
        """
        if options is None:
            options = {}
        self.state = self.implementation.connector_initialize(options)

    def load_users_and_groups(self, groups, extended_attributes=None, all_users=True):
        """
        :type groups: list(str)
        :type extended_attributes: Optional(list(str))
        :type all_users: bool
        :rtype (bool, iterable(dict))
        """
        if extended_attributes is None:
            extended_attributes = []
        return self.implementation.connector_load_users_and_groups(self.state,
                                                                   groups=groups,
                                                                   extended_attributes=extended_attributes,
                                                                   all_users=all_users)
