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

import csv
import datetime
import os

import user_sync.error

def open_file(name, mode, buffering = -1):
    '''
    :type name: str
    :type mode: str
    :type buffering: int
    '''
    try:
        return open(str(name), mode, buffering)
    except IOError as e:
        raise user_sync.error.AssertionException(str(e))

def normalize_string(string_value):
    '''
    Normalize a unicode or regular string
    :param string_value: either a unicode or regular string or None
    :return: the same type that came in
    '''
    return string_value.strip().lower() if string_value is not None else None
    
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

def iter_csv_rows(file_path, delimiter = None, recognized_column_names = None, logger = None):
    '''
    :type file_path: str
    :type delimiter: str
    :type recognized_column_names: list(str)
    :type logger: logging.Logger
    '''
    with open_file(file_path, 'r', 1) as input_file:
        if (delimiter == None):
            delimiter = guess_delimiter_from_filename(file_path)
        reader = csv.DictReader(input_file, delimiter = delimiter)

        if (recognized_column_names != None):
            unrecognized_column_names = [column_name for column_name in reader.fieldnames if column_name not in recognized_column_names] 
            if (len(unrecognized_column_names) > 0 and logger != None):
                logger.warn("In file '%s': unrecognized column names: %s", file_path, unrecognized_column_names)

        for row in reader:
            yield row
            
class JobStats(object):
    line_left_count = 10
    line_width = 60
    
    def __init__(self, name, divider = '-'):
        self.name = name
        self.divider = divider
        self.start_time = datetime.datetime.now()
        
    def create_divider(self, header):        
        divider = self.divider 

        left_count = JobStats.line_left_count
        left_side = left_count * divider        
        right_count = (JobStats.line_width - len(header)) / len(divider) - left_count
        if (right_count < 0):
            right_count = 0
        right_side = right_count * divider
        line = left_side + header + right_side
        return line        
    
    def log_start(self, logger):
        header = " Start %s " % self.name
        line = self.create_divider(header)        
        logger.info(line)
        
    def log_end(self, logger):
        end_time = datetime.datetime.now()
        rounded_time = datetime.timedelta(seconds=(end_time - self.start_time).seconds)
        header = " End %s (Total time: %s) " % (self.name, rounded_time)        
        line = self.create_divider(header)
        logger.info(line)
