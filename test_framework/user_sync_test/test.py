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
import os
import yaml
import subprocess
import server
import error
import shlex
import six
import logging

TEST_SET_TEMPLATE_KEYS = {
    '/user_sync/user_sync_path': (True, False, "../../dist/user-sync"),
    }

TEST_TEMPLATE_KEYS = {
    '/user_sync/record_output_filename': (False, False, "record/output.txt"),
    '/user_sync/canned_output_filename': (False, False, "canned/output.txt"),
    '/server_profile/get_filename': (False, False, 'record/get.yml'),
    '/server_profile/post_filename': (False, False, 'record/post.yml')
    }

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
        :param template_keys: a dict whose keys are "template_keys" such as /key1/key2/key3
                              and whose values are tuples: (must_exist, can_have_subdict, default_val)
                              which are options on the value of the key whose values
                              are path expanded: must the path exist, can it be a list of paths
                              that contains sub-dictionaries whose values are paths, and
                              does the key have a default value so that must be added to
                              the dictionary if there is not already a value found.
        '''
        cls.filepath = os.path.abspath(filename)
        cls.filename = os.path.split(cls.filepath)[1]
        cls.dirpath = os.path.dirname(cls.filepath)
        if not os.path.isfile(cls.filepath):
            raise error.AssertionException('No such configuration file: %s' % (cls.filepath))

        with open(filename, 'r', 1) as input_file:
            yml = yaml.load(input_file)

        for template_key, options in template_keys.iteritems():
            cls.key_path = template_key
            keys = template_key.split('/')
            cls.process_path_key(yml, keys, 1, *options)
        return yml

    @classmethod
    def process_path_key(cls, dictionary, keys, level, must_exist, can_have_subdict, default_val):
        '''
        this function is given the list of keys in the current key_path, and searches recursively into the given
        dictionary until it finds the designated value, and then resolves relative values in that value to abspaths
        based on the current filename. If a default value for the key_path is given, and no value is found in the
        dictionary, then the key_path is added to the dictionary with the expanded default value.
        type dictionary: dict
        type keys: list
        type level: int
        type must_exist: boolean
        type can_have_subdict: boolean
        type default_val: any
        '''
        if level == len(keys)-1:
            key = keys[level]
            # if a wildcard is specified at this level, that means we should
            # process all keys as path values
            if key == "*":
                for key, val in dictionary.iteritems():
                    dictionary[key] = cls.process_path_value(val, must_exist, can_have_subdict)
            elif dictionary.has_key(key):
                dictionary[key] = cls.process_path_value(dictionary[key], must_exist, can_have_subdict)
            elif default_val:
                dictionary[key] = cls.relative_path(default_val, must_exist)
        elif level < len(keys)-1:
            key = keys[level]
            # if a wildcard is specified at this level, this indicates this
            # should select all keys that have dict type values, and recurse
            # into them at the next level
            if key == "*":
                for key in dictionary.keys():
                    if isinstance(dictionary[key],dict):
                        cls.process_path_key(dictionary[key], keys, level+1, must_exist, can_have_subdict, default_val)
            elif dictionary.has_key(key):
                if isinstance(dictionary[key], dict):
                    cls.process_path_key(dictionary[key], keys, level+1, must_exist, can_have_subdict, default_val)
            elif default_val:
                dictionary[key] = {}
                cls.process_path_key(dictionary[key], keys, level+1, must_exist, can_have_subdict, default_val)

    @classmethod
    def process_path_value(cls, val, must_exist, can_have_subdict):
        '''
        does the relative path processing for a value from the dictionary, which can be a string, a list of strings, or
        a list of strings and "tagged" strings (sub-dictionaries whose values are strings)
        :param key: the key whose value we are processing, for error messages
        :param val: the value we are processing, for error messages
        '''
        if isinstance(val, six.types.StringTypes):
            return cls.relative_path(val, must_exist)
        elif isinstance(val, list):
            vals = []
            for entry in val:
                if can_have_subdict and isinstance(entry, dict):
                    for subkey, subval in entry.iteritems():
                        vals.append({subkey: cls.relative_path(subval, must_exist)})
                else:
                    vals.append(cls.relative_path(entry, must_exist))
            return vals

    @classmethod
    def relative_path(cls, val, must_exist):
        '''
        returns an absolute path that is resolved relative to the file being loaded
        '''
        if not isinstance(val, six.types.StringTypes):
            raise error.AssertionException("Expected pathname for setting %s in config file %s" %
                                     (cls.key_path, cls.filename))
        if cls.dirpath and not os.path.isabs(val):
            val = os.path.abspath(os.path.join(cls.dirpath, val))
        if must_exist and not os.path.isfile(val):
            raise error.AssertionException('In setting %s in config file %s: No such file %s' %
                                     (cls.key_path, cls.filename, val))
        return val



class UserSyncTestSet:
    def __init__(self, config_filename, program_config):
        '''
        Sets up a user sync test set, given a path to the test set's configuration file.
        :type config_filename: str
        '''
        config_filename = os.path.abspath(config_filename)
        self.test_set_path = os.path.dirname(config_filename)

        test_set_config = ConfigFileLoader.load_from_yaml(config_filename, TEST_SET_TEMPLATE_KEYS)

        self.test_set_config = program_config.copy()
        self.test_set_config.update({
            'user_sync_path': test_set_config['user_sync']['user_sync_path']
        })

        self.server_config = {
            'pass_through': program_config['record_mode'],
            'proxy_host': test_set_config['umapi']['proxy_host'],
            'destination_host': test_set_config['umapi']['destination_host']
        }

    def run(self):
        '''
        Runs all the tests in the test set. It first identifies tests by searching in the test set folder for all
        sub-folders containing the file test-config.yml. It then goes through the tests configurations individually, and
        creates and runs each test configuration instance.
        '''
        self.test_paths = [os.path.join(self.test_set_path,f) for f in os.listdir(self.test_set_path) if os.path.isfile(os.path.join(self.test_set_path,f,'test-config.yml'))]
        for test_path in self.test_paths:
            print 'test: ' + test_path
            test = UserSyncTest(test_path, self.options, self.server_options)
            if self.options['record_mode']:
                test.record()
            else:
                test.play()

class UserSyncTest:
    def __init__(self, config_path, options, server_options):
        '''
        Sets up a user sync test, given a path to the test's configuration file.
        :type config_path: str
        '''
        self.options = options
        self.server_options = server_options
        self.server_options['test_folder_path'] = config_path
        self.config = ConfigFileLoader.load_from_yaml(os.path.join(config_path, 'test-config.yml'), TEST_TEMPLATE_KEYS)

        self.options['user_sync_args'] = self.config['user_sync']['arguments']
        self.options['record_output_filename'] = self.config['user_sync']['record_output_filename']
        self.options['canned_output_filename'] = self.config['user_sync']['canned_output_filename']
        self.server_options['get_filename'] = self.config['server_profile']['get_filename']
        self.server_options['post_filename'] = self.config['server_profile']['post_filename']

        self.logger = logging.getLogger('user-sync-test')

    def removeFileIfExists(self,filename):
        if os.path.exists(filename):
            os.remove(filename)

    def record(self):
        '''
        Runs the test in record mode. It first clears the record folder, then sets the server in pass-through mode.
        user-sync is then invoked with the arguments specified in the configuration file, and requests and responses are
        recorded until user-sync returns.
        '''
        self.removeFileIfExists(self.server_options['get_filename'])
        self.removeFileIfExists(self.server_options['post_filename'])

        service = server.TestService(self.server_options)
        service.run()

        arguments = [self.options['user_sync_path']]
        arguments.extend(shlex.split(self.config['user_sync']['arguments']))

        self.logger.info("recording test: %s %s" % (self.options['user_sync_path'], self.config['user_sync']['arguments']))


        output = subprocess.check_output(arguments, cwd=self.server_options['test_folder_path'])
        print output
        
        service.stop()
        
    def play(self):
        '''
        Runs the test in playback mode. This simply sets the test server to use the recorded data, and launches the
        user-sync tool to --bypass-authentication-mode.
        '''
        service = server.TestService(self.server_options)
        service.run()

        arguments = [self.options['user_sync_path']]
        arguments.extend(['--bypass-authentication-mode'])
        arguments.extend(shlex.split(self.config['user_sync']['arguments']))

        print "play: %s %s" % (self.options['user_sync_path'], self.config['user_sync']['arguments'])
        
        output = subprocess.check_output(arguments, cwd=self.server_options['test_folder_path'])
        print output

        service.stop()
