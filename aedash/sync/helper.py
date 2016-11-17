
import os

import aedash.sync.error

def open_file(name, mode, buffering = -1):
    '''
    :type name: str
    :type mode: str
    :type buffering: int
    '''
    try:
        return open(name, mode, buffering)
    except IOError as e:
        raise aedash.sync.error.AssertionException(str(e))

def normalize_string(string_value):
    '''
    :type string_value: str
    '''
    return string_value.strip().lower() if string_value != None else None    
    
def guess_delimiter_from_filename(filename):
    '''
    :type filename
    :rtype str
    '''
    _base_name, extension = os.path.os.path.splitext(filename)
    normalized_extension = normalize_string(extension)
    if (normalized_extension == '.csv'):
        return ','
    if (normalized_extension == '.tsv'):
        return '\t'
    return '\t'