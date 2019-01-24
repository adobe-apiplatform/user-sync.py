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

import json
import re
import os
import error

def val_type_pre(val):
    val_type = type(val)
    if val_type == int:
        return 0
    elif val_type == long:
        return 1
    elif val_type == float:
        return 2
    elif val_type == str:
        return 3
    elif val_type == unicode:
        return 4
    elif val_type == list:
        return 5
    elif val_type == dict:
        return 6
    raise AssertionError("Unrecognized value type %s" % val_type)


def deep_compare(val1, val2, ignore_paths=set()):
    '''
    Deep compare two values, to determine the whether the first value is greater than or less than the second. The
    comparison order is as follows:
    
    if the two values differ in terms of type, the result is determined by the following list of types in order of
    precedence from least to greatest:
    int
    long
    float
    str
    unicode
    list
    dict
    
    if two lists are being compared, their lengths are first compared. If one list is longer than the other, the longer
    one is considered greater. Otherwise if both lists are the same length, the list items are compared directly, first
    by their type in the same fashion as previously defined, then by their value if the types are the same. Value
    comparisons are recursively if the values are lists or dicts.
    
    if two dicts are being compared, their key count is first compared. If one key count is greater than the other, the
    longer one is considered greater. If their key count is equivalent, the key names are sorted then compared. If
    the key names are identical, the their values are compared.
    
    any other types are compared by their direct values.
    
    :param val1: any value as the first value to compare
    :param val2: any value as the second value to compare
    :param ignore_paths: set containing strings representing paths who's corresponding values are ignored in the
        comparison process.
    :return: -1 if val1 is less than val2, 0 if val1 and val2 are equivalent, 1 if val1 is greater than val2
    '''
    def deep_compare_items(val1, val2, path):
        if type(val1) is not type(val2):
            return 1 if val_type_pre(val1) > val_type_pre(val2) else -1

        if isinstance(val1, list):
            for item1, item2 in zip(val1, val2):
                res = deep_compare_items(item1, item2, "%s/*" % (path))
                if res:
                    return res
            return 0

        if isinstance(val1, dict):
            keys1 = val1.keys()
            keys2 = val2.keys()
            if not len(keys1) == len(keys2):
                return 1 if len(keys1) > len(keys2) else -1

            keys1.sort()
            keys2.sort()
            for key1, key2 in zip(keys1, keys2):
                if not key1 == key2:
                    return 1 if key1 > key2 else -1

            for key in keys1:
                sub_path = "%s/%s" % (path, key)
                if not sub_path in ignore_paths:
                    res = deep_compare_items(val1[key], val2[key], "%s/%s" % (path,key))
                    if res:
                        return res
            return 0

        if not val1 == val2:
            return 1 if val1 > val2 else -1
        return 0

    return deep_compare_items(val1, val2, "")

def sort_and_deep_compare_lists(list1, list2):
    list1.sort(deep_compare)
    list2.sort(deep_compare)

    return deep_compare(list1, list2)

class JSONBuilder(object):
    def __init__(self):
        self.json_val = []

    def extend_with_json_string(self, json_str):
        val = json.loads(json_str)

        if isinstance(val, list):
            self.json_val.extend(val)
        elif isinstance(val, dict):
            self.json_val.append(val)
        else:
            raise AssertionError("Unrecognized json value type.")


class StringTransformer:
    def __init__(self, str_expr, out_fmt):
        '''
        Defines a string transformer where the regular expression is applied to the string, and applied to the
        specified output format string.
        :type str_expr: str defining the regular expression which is used to apply to the input string.
        :type out_fmt: str defining the format of the string to output. There must be one %s per capture group defined
                       in str_extr
        '''
        self.matcher = re.compile(str_expr)
        self.out_fmt = out_fmt

    def transform(self, s):
        '''
        Tries to apply the matcher to the supplied string. If successful, a formatted string is returned, otherwise
        None is returned.
        :param s: str representing the string to transform
        :return: str representing the formatted string, or None if the match failed
        '''
        m = self.matcher.match(s)
        if m:
            return self.out_fmt % m.groups()
        return None

class JobStats:
    test_success_count = 0
    test_fail_count = 0
    test_skip_count = 0

    @classmethod
    def inc_test_success_count(cls):
        JobStats.test_success_count += 1

    @classmethod
    def inc_test_fail_count(cls):
        JobStats.test_fail_count += 1

    @classmethod
    def inc_test_skip_count(cls):
        JobStats.test_skip_count += 1

def read_lines(filename):
    if not os.path.isfile(filename):
        raise error.AssertionException('File "%s" not found.' % (filename))
    with open(filename, 'r') as file:
        return file.read().splitlines()


def verify_unordered_text_files(filename1, filename2, line_transform_map=[]):
    '''
    Compares the contents of the specified output filenames. The comparison is made by first stripping out the log entry
    timestamp, as well as certain string occurances, such as timestamps within the entry body, the actionID, and
    characters enclosed in double square brackets. Both the output file as well as the recorded output file are 
    processed in this manner, then both have their lines sorted, then a line by line comparison is made. If a mismatch
    is found, an error is thrown detailing the two output lines and their respective line numbers.
    :type filename1: str
    :type filename2: str
    :type live_output_filename: str
    '''
    lines1 = read_lines(filename1)
    lines2 = read_lines(filename2)

    def transform_lines(lines):
        '''
        Transforms the specified list of strings to a a list of strings in which each string is passed through the
        transform map.
        :param lines: list(str)
        :return: list(str)
        '''
        lines_out = []
        for line in lines:
            line_out = None
            for transform in line_transform_map:
                line_out = transform.transform(line)
                if line_out is not None:
                    break
            lines_out.append(line_out if line_out is not None else line)
        return lines_out

    def compare_line_tuple(line_tuple1, line_tuple2):
        index1, line1 = line_tuple1
        index2, line2 = line_tuple2
        return 1 if line1 > line2 else -1 if line1 < line2 else 0

    tlines1 = transform_lines(list(lines1))
    tlines1 = zip(range(0, len(tlines1)), tlines1)
    tlines1.sort(compare_line_tuple)
    tlines2 = transform_lines(list(lines2))
    tlines2 = zip(range(0, len(tlines2)), tlines2)
    tlines2.sort(compare_line_tuple)

    for line_tuple1, line_tuple2 in zip(tlines1, tlines2):
        if not compare_line_tuple(line_tuple1, line_tuple2)==0:
            index1, line1 = line_tuple1
            index2, line2 = line_tuple2
            raise error.VerificationException('Output line mismatch\n%s (LINE %d):\n%s\n%s (LINE %d):\n%s' % (filename1, index1, lines1[index1], filename2, index2, lines2[index2]))

    if not len(lines1) == len(lines2):
        raise error.VerificationException('Expected %d output lines, got %d lines.' % (len(lines2), len(lines1)))

def verify_text_files(filename1, filename2):
    '''
    Verifies that the text lines of files indicated by the specified file names match exactly.
    :type filename1: str
    :type filename2: str
    '''
    lines1 = read_lines(filename1)
    lines2 = read_lines(filename2)

    line_index = 0
    for line1, line2 in zip(lines1, lines2):
        if not line1 == line2:
            raise error.VerificationException('Output line mismatch\n%s (LINE %d):\n%s\n%s (LINE %d):\n%s' % (filename1, line_index, line1, filename2, line_index, line2))
        line_index += 1

    if not len(lines1) == len(lines2):
        raise error.VerificationException('Expected %d output lines, got %d lines.' % (len(lines1), len(lines2)))
