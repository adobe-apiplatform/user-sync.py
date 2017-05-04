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
import shutil
import six
import re
import logging

TEST_SET_TEMPLATE_KEYS = {
    '/user_sync/user_sync_path': (True, False, "../../dist/user-sync"),
    }

TEST_TEMPLATE_KEYS = {
    '/user_sync/live/working_dir': (False, False, "live"),
    '/user_sync/live/output_dir': (False, False, "live/out"),
    '/user_sync/recorded/working_dir': (False, False, "rec"),
    '/user_sync/recorded/output_dir': (False, False, "rec/out"),
    '/server_profile/cassette_filename': (False, False, 'live/cassette.yml'),
    }

IS_NT_PLATFORM = os.name == 'nt'

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
            (must_exist, can_have_subdict, default_val) which are options on the value of the key whose values are path
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
            # if a wildcard is specified at this level, that means we should process all keys as path values
            if key == "*":
                for key, val in dictionary.iteritems():
                    dictionary[key] = cls.process_path_value(val, must_exist, can_have_subdict)
            elif dictionary.has_key(key):
                dictionary[key] = cls.process_path_value(dictionary[key], must_exist, can_have_subdict)
            elif default_val:
                dictionary[key] = cls.relative_path(default_val, must_exist)
        elif level < len(keys)-1:
            key = keys[level]
            # if a wildcard is specified at this level, this indicates this should select all keys that have dict type
            # values, and recurse into them at the next level
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
    def __init__(self, config_filename, config):
        '''
        Sets up a user sync test set, given a path to the test set's configuration file. This basically maps
        configuration settings from the configuration file and options constructed from the command line arguments to
        test set and server configuration dictionary objects. Also, the user sync path is examined to determine if
        the user-sync tool can be invoked directly, or needs to be invoked through python, and sets up the
        test set configuration accordingly.
        :type config_filename: str
        '''
        self.logger = logging.getLogger('user-sync-test-set')

        config_filename = os.path.abspath(config_filename)
        test_set_path = os.path.dirname(config_filename)
        test_set_config = ConfigFileLoader.load_from_yaml(config_filename, TEST_SET_TEMPLATE_KEYS)

        user_sync_common_args = test_set_config['user_sync']['common_arguments'] if 'common_arguments' in test_set_config['user_sync'] else None
        user_sync_path = test_set_config['user_sync']['user_sync_path']
        if re.match(r"^.*\.pex$", user_sync_path, re.IGNORECASE):
            user_sync_common_args = user_sync_path if not user_sync_common_args else "\"%s\" %s" % (user_sync_path, user_sync_common_args)
            user_sync_path = "python"

        self.test_set_config = config
        self.test_set_config.update({
            'user_sync_path': user_sync_path,
            'user_sync_common_args': user_sync_common_args
        })

        self.server_config = {
            'pass_through': config['record_mode'],
            'proxy_host': test_set_config['umapi']['proxy_host'],
            'destination_host': test_set_config['umapi']['destination_host']
        }

        if self.test_set_config['test_name']:
            self.test_paths = [os.path.join(test_set_path, self.test_set_config['test_name'])]
        else:
            self.test_paths = [os.path.join(test_set_path,f) for f in os.listdir(test_set_path) if os.path.isfile(os.path.join(test_set_path,f,'test-config.yml'))]

        self.success_count = 0
        self.fail_count = 0

    def run(self):
        '''
        Runs all the tests in the test set. It first identifies tests by searching in the test set folder for all
        sub-folders containing the file test-config.yml. It then goes through the tests configurations individually, and
        creates and runs each test configuration instance.
        '''
        for test_path in self.test_paths:
            test = UserSyncTest(test_path, self.test_set_config, self.server_config)
            if self.test_set_config['record_mode']:
                test.run_live()
            else:
                test.run()

            if test.success:
                self.success_count += 1
            else:
                self.fail_count += 1

class StringComparator:
    def __init__(self, str1_expr, str1_args, str2_expr, str2_args):
        '''
        Defines a string comparator where their equality is determined by the specified regular expressions. The line
        arguments parameters are used as format parameters that are applied to the string before performing the matches.
        Capture groups define in string1_expr must be matched exactly in the second string.
        :type str1_expr: str defining the regular expression for the first line used for comparison. You can define
            capture groups that can be used for one to one comparison in the second line.
        :type str1_args: list(str) defining the arguments used in formatting the str1_expr, which is applied just
            before running the regular expression match.
        :type str2_expr: str defining the regular expression for the second line used for the comparison.
        :type str2_args: list(str) like str1_expr, defines the arguments used in formatting the str2_expr. You can
            add None elements in the list, which will be populated with the capture group values from the str1_expr
            match just before applying the arguments to the str2_expr formatting.
        '''
        self.str1_expr = str1_expr
        self.str1_args = str1_args
        self.str2_expr = str2_expr
        self.str2_args = str2_args

    def compare(self, str1, str2):
        '''
        Compares two lines using the comparator's str1/str2 expressions. Capture groups specified in str1 expression
        are applied to str2 arguments, where any None entry is replaced with a capture group value in order of
        occurance.
        The expression for str1 is first matched. If that succeeds, the expression for str 2 is matched with the 
        specified arguements and capture groups applied. The compare is considered successful if the second match
        succeeds.
        :param str1: str representing the first string to match
        :param str2: str representing the second string that the first will me matched to.
        :return: bool
        '''
        m = re.match(self.str1_expr % tuple(self.str1_args), str1)
        if m:
            str1_groups = m.groups()
            str2_args = list(self.str2_args)
            str2_group_indexes = [index for index in range(1, len(str2_args)) if str2_args[index] is None]

            if not (len(str1_groups) == len(str2_group_indexes)):
                raise error.AssertionException(
                    'Output compare error: expected %d captures, got %d captures.' % (len(str2_group_indexes), len(str1_groups)))

            for str1_group, str2_group_index in zip(str1_groups, str2_group_indexes):
                str2_args[str2_group_index] = re.escape(str1_group)

            if re.match(self.str2_expr % tuple(str2_args), str2):
                return True

        return False


class UserSyncTest:
    def __init__(self, config_path, test_set_config, server_config):
        '''
        Sets up a user sync test, given a path to the test's configuration file.
        :type config_path: str
        '''
        config = ConfigFileLoader.load_from_yaml(os.path.join(config_path, 'test-config.yml'), TEST_TEMPLATE_KEYS)

        self.server_config = server_config
        self.server_config.update({
            'test_folder_path': config_path,
            'cassette_filename': config['server_profile']['cassette_filename'],
        })

        self.test_config = test_set_config.copy()
        self.test_config.update({
            'config_path': config_path,
            'user_sync_args': config['user_sync']['arguments'],
            'live_working_dir': config['user_sync']['live']['working_dir'],
            'live_output_dir': config['user_sync']['live']['output_dir'],
            'rec_working_dir': config['user_sync']['recorded']['working_dir'],
            'rec_output_dir': config['user_sync']['recorded']['output_dir'],
        })

        self.logger = logging.getLogger('user-sync-test')
        self.success = False

    def _reset_output_file(self,filename):
        '''
        Resets and output file by first removing the file with the specified filename if it exists, then creating the
        intermediate folders if they don't exist.
        :type filename: str
        '''
        if os.path.isfile(filename):
            os.remove(filename)
        elif os.path.isdir(filename):
            shutil.rmtree(filename)

        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def _run(self, args, working_dir, output_filename):
        '''
        Runs the test given the command line arguments, and the output filename. The output file is deleted first if
        it exists, then the user-sync test service is started. The test service is stopped once the user-sync command
        has been run.
        :type args: list(str) representing the components of the command line argument.
        :c output_filename: str represents the filename of the file to write the command line output to.
        '''
        self.logger.info("%s" % (' '.join(args)))

        self._reset_output_file(output_filename)

        service = server.UserSyncTestService(self.server_config)
        service.run()

        with open(output_filename, 'w') as output_file:
            subprocess.call(args, cwd=working_dir, stdout=output_file, stderr=output_file, shell=IS_NT_PLATFORM)

        service.stop()

    def _compare_output(self, live_output_filename, rec_output_filename, user_sync_path):
        '''
        Compares the contents of the specified output filenames. Contents are compared by ignoring the timestamp,
        references to the total time, and the --bypass-authentication-mode part of the command line arguments. If a
        difference is encountered, an exception is raised detailing the line number and the mismatched lines.
        :type live_output_filename: str
        :type rec_output_filename: str
        '''
        # log format defined in app.py (date, time, pid)
        timestamp_re = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \d+'

        LINE_COMPARE_MAP = [
            StringComparator(
                r"^%s INFO main - %s (.*)$", [timestamp_re, re.escape(user_sync_path)],
                r"^%s INFO main - %s --bypass-authentication-mode %s$", [timestamp_re, re.escape(user_sync_path), None]
            ),
            StringComparator(
                r"^%s (.*)\(Total time: \d:\d\d:\d\d\)(.*)$", [timestamp_re],
                r"^%s %s\(Total time: \d:\d\d:\d\d\)%s$", [timestamp_re, None, None]
            ),
            StringComparator(
                r"^%s (.*)$", [timestamp_re],
                r"^%s %s$", [timestamp_re, None]
            ),
        ]

        if not os.path.isfile(live_output_filename):
            raise error.AssertionException('Output compare error: recorded output file "%s" not found.'% (live_output_filename))
        if not os.path.isfile(rec_output_filename):
            raise error.AssertionException('Output compare error: canned output file "%s" not found.' % (rec_output_filename))

        with open(live_output_filename, 'r') as rfile:
            rlines = rfile.readlines()
        with open(rec_output_filename, 'r') as cfile:
            clines = cfile.readlines()

        if not (len(rlines) == len(clines)):
            raise error.AssertionException('Output compare error: expected %d lines, got %d lines.' % (len(rlines), len(clines)))

        line_index = 0
        for rline, cline in zip(rlines, clines):
            matched = False
            for comparator in LINE_COMPARE_MAP:
                if comparator.compare(rline, cline):
                    matched = True
                    break

            if not matched:
                raise error.AssertionException('Output compare error: unexpected output at line %d\nrecord: %s\noutput: %s' % (line_index, rline, cline))

            line_index = line_index + 1

    def run_live(self):
        '''
        Runs the test in record mode. It first removes the existing recorded data, then runs the user-sync test service
        in record mode (allowing the user-sync service to pass through the service and connect to the live Adobe
        server). It ends by saving the recorded requests and responses, as well as the user-sync tool output.
        '''
        try:
            self._reset_output_file(self.server_config['cassette_filename'])
            self._reset_output_file(self.test_config['live_output_dir'])

            args = [self.test_config['user_sync_path']]
            if self.test_config['user_sync_common_args']:
                args.extend(shlex.split(self.test_config['user_sync_common_args'], posix=not IS_NT_PLATFORM))
            args.extend(shlex.split(self.test_config['user_sync_args'], posix=not IS_NT_PLATFORM))

            output_filename = os.path.join(self.test_config['live_output_dir'], 'out.txt')
            self._run(args, self.test_config['live_working_dir'], output_filename)

            self.logger.info('successfully recorded %s' % (self.test_config['config_path']))
            self.success = True
        except error.AssertionException as e:
            if not e.is_reported():
                self.logger.error('user-sync test error: %s' % (e.message))
                e.set_reported()

    def run(self):
        '''
        Runs the test using canned data. This simply sets the user-sync test service to use the recorded data, instead
        of connecting to the live Adobe server, and launches the user-sync tool with --bypass-authentication-mode. Then
        test ends by saving the user-sync tool output to the configured path.
        '''
        try:
            self._reset_output_file(self.test_config['rec_output_dir'])

            args = [self.test_config['user_sync_path']]
            if self.test_config['user_sync_common_args']:
                args.extend(shlex.split(self.test_config['user_sync_common_args'], posix=not IS_NT_PLATFORM))
            args.extend(['--bypass-authentication-mode'])
            args.extend(shlex.split(self.test_config['user_sync_args'], posix=not IS_NT_PLATFORM))

            live_output_filename = os.path.join(self.test_config['live_output_dir'], 'out.txt')
            output_filename = os.path.join(self.test_config['rec_output_dir'], 'out.txt')
            self._run(args, self.test_config['rec_working_dir'], output_filename)

            self._compare_output(live_output_filename, output_filename, self.test_config['user_sync_path'])

            self.logger.info('successfully ran and verified output for %s' % (self.test_config['config_path']))
            self.success = True
        except error.AssertionException as e:
            if not e.is_reported():
                self.logger.error('user-sync test error: %s' % (e.message))
                e.set_reported()
