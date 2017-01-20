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

UMAPI_CREDENTIAL_TYPE = "Adobe_UMAPI"
DIRECTORY_CREDENTIAL_TYPE = "Directory"

def get_credentials(credential_type, credential_id, **kwArgs):
    '''
    This allows a customer to customize how credentials are fetched.
    For the UMAPI related credential, the application will specify credential_type as "Adobe_UMAPI" and credential_id would 
    be the org id.
    For directory related credential like LDAP, the credential_type would be "Directory" and the credential_id would be 
    the type of directory connector like ldap, csv, etc.   
    kwArgs is a dictionary containing extra data, with:
    - 'config' being the current config for the credential to retrieve.
    - 'config_loader' being the instance of the loader
    
    The application supports these return types:
    - config object in dict
    - file path to a yaml file containing a config object
    - None
    
    :type credential_type: str
    :type id: str
    :type kwArgs: dict
    :rtype dict | str | None
    '''
    return None
    
