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
import error
import yaml
import six

class ConfigFileLoader:
    # these are set by load_from_yaml to hold the current state of what key_path is being searched for in what file in
    # what directory
    filepath = None # absolute path of file currently being loaded
    filename = None # filename of file currently being loaded
    dirpath = None  # directory path of file currently being loaded
    key_path = None # the full pathname of the setting key being processed

    @classmethod
    def load_from_yaml(cls, filename, template_keys):
        '''
        loads a yaml file, processes the loaded dict given the specified template keys. Essentially the same as the
        ConfigFileLoader in the UserSync app.
        :param filename: the file to load yaml from
        :param template_keys: a dict whose keys are "template_keys" such as /key1/key2/key3 and whose values are tuples:
            (path_must_exist, is_path, default_val) which are options on the value of the key whose values are path
            expanded: must the path exist, can it be a list of paths that contains sub-dictionaries whose values are
            paths, and does the key have a default value so that must be added to the dictionary if there is not already
            a value found.
        '''
        cls.filepath = os.path.abspath(filename)
        cls.filename = os.path.split(cls.filepath)[1]
        cls.dirpath = os.path.dirname(cls.filepath)

        if not os.path.isfile(cls.filepath):
            raise error.AssertionException('No such configuration file: %s' % (cls.filepath))

        with open(filename, 'r', 1) as input_file:
            yml = yaml.load(input_file)
            if yml is None:
                yml = {}

        for template_key, options in template_keys.iteritems():
            cls.key_path = template_key
            keys = template_key.split('/')
            cls.process_path_key(yml, keys, 1, *options)
        return yml

    @classmethod
    def process_path_key(cls, dictionary, keys, level, is_path, path_must_exist, default_val=None):
        '''
        this function is given the list of keys in the current key_path, and searches recursively into the given
        dictionary until it finds the designated value, and then resolves relative values in that value to abspaths
        based on the current filename. If a default value for the key_path is given, and no value is found in the
        dictionary, then the key_path is added to the dictionary with the expanded default value.
        type dictionary: dict
        type keys: list
        type level: int
        type must_exist: boolean
        type is_path: boolean
        type default_val: any
        '''
        if level == len(keys)-1:
            key = keys[level]
            # if a wildcard is specified at this level, that means we should process all keys as path values
            if key == "*":
                for key, val in dictionary.iteritems():
                    dictionary[key] = cls.process_path_value(val, is_path, path_must_exist)
            elif dictionary.has_key(key):
                dictionary[key] = cls.process_path_value(dictionary[key], is_path, path_must_exist)
            else:
                if is_path and default_val is not None:
                    dictionary[key] = cls.relative_path(default_val, path_must_exist)
                else:
                    dictionary[key] = default_val
        elif level < len(keys)-1:
            key = keys[level]
            # if a wildcard is specified at this level, this indicates this should select all keys that have dict type
            # values, and recurse into them at the next level
            if key == "*":
                for key in dictionary.keys():
                    if isinstance(dictionary[key],dict):
                        cls.process_path_key(dictionary[key], keys, level+1, is_path, path_must_exist, default_val)
            elif dictionary.has_key(key):
                if isinstance(dictionary[key], dict):
                    cls.process_path_key(dictionary[key], keys, level+1, is_path, path_must_exist, default_val)
                elif not dictionary[key]:
                    dictionary[key] = {}
                    cls.process_path_key(dictionary[key], keys, level+1, is_path, path_must_exist, default_val)
            else:
                dictionary[key] = {}
                cls.process_path_key(dictionary[key], keys, level+1, is_path, path_must_exist, default_val)

    @classmethod
    def process_path_value(cls, val, is_path, path_must_exist):
        '''
        does the relative path processing for a value from the dictionary, which can be a string, a list of strings, or
        a list of strings and "tagged" strings (sub-dictionaries whose values are strings)
        :param key: the key whose value we are processing, for error messages
        :param val: the value we are processing, for error messages
        '''
        if isinstance(val, six.types.StringTypes):
            if is_path:
                return cls.relative_path(val, path_must_exist)
            else:
                return val
        return val

    @classmethod
    def relative_path(cls, val, path_must_exist):
        '''
        returns an absolute path that is resolved relative to the file being loaded
        '''
        if not isinstance(val, six.types.StringTypes):
            raise error.AssertionException("Expected pathname for setting %s in config file %s" %
                                     (cls.key_path, cls.filename))
        if cls.dirpath and not os.path.isabs(val):
            val = os.path.abspath(os.path.join(cls.dirpath, val))
        if path_must_exist and not os.path.isfile(val):
            raise error.AssertionException('In setting %s in config file %s: No such file %s' %
                                     (cls.key_path, cls.filename, val))
        return val
