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

import user_sync.error
import user_sync.helper

ENTERPRISE_IDENTITY_TYPE = 'enterpriseID'
FEDERATED_IDENTITY_TYPE = 'federatedID'
ADOBEID_IDENTITY_TYPE = 'adobeID'

NORMALIZED_IDENTITY_TYPE_MAP = {
    user_sync.helper.normalize_string(ADOBEID_IDENTITY_TYPE): ADOBEID_IDENTITY_TYPE,
    user_sync.helper.normalize_string(ENTERPRISE_IDENTITY_TYPE): ENTERPRISE_IDENTITY_TYPE,
    user_sync.helper.normalize_string(FEDERATED_IDENTITY_TYPE): FEDERATED_IDENTITY_TYPE,
}


def parse_identity_type(value, message_format=None):
    """
    :type value: basestring
    :type message_format: basestring
    :rtype str
    """
    result = None
    if value is not None:
        normalized_value = user_sync.helper.normalize_string(value)
        result = NORMALIZED_IDENTITY_TYPE_MAP.get(normalized_value)
        if result is None:
            validation_message = 'Unrecognized identity type: "%s"' % value
            message = validation_message if message_format is None else message_format % validation_message
            raise user_sync.error.AssertionException(message)
    return result
