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
import vcr

import helper

TEST_SET_TEMPLATE_KEYS = {
    '/user_sync/user_sync_path': (True, False, "../../dist/user-sync"),
    }

TEST_TEMPLATE_KEYS = {
    '/user_sync/live/working_dir': (False, False, "live"),
    '/user_sync/live/output_dir': (False, False, "live/out"),
    '/user_sync/test/working_dir': (False, False, "test"),
    '/user_sync/test/output_dir': (False, False, "test/out"),
    '/server/cassette_filename': (False, False, 'live/cassette.yml'),
    }

TEST_CONFIG_FILENAME = 'test-config.yml'

REQUEST_JSON_IGNORE_PATHS = set(
    '/do/requestID'
)

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
                elif not dictionary[key]:
                    dictionary[key] = {}
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


class TestSuite:
    def __init__(self, config_filename, config):
        '''
        Sets up a user sync test set, given a path to the test set's configuration file. This basically maps
        configuration settings from the configuration file and options constructed from the command line arguments to
        test set and server configuration dictionary objects. Also, the user sync path is examined to determine if
        the user-sync tool can be invoked directly, or needs to be invoked through python, and sets up the
        test set configuration accordingly.
        :type config_filename: str
        '''
        self.logger = logging.getLogger('test-suite')

        config_filename = os.path.abspath(config_filename)
        test_set_config = ConfigFileLoader.load_from_yaml(config_filename, TEST_SET_TEMPLATE_KEYS)
        self.test_suite_path = test_suite_path = os.path.dirname(config_filename)

        user_sync_common_args = test_set_config['user_sync']['common_arguments'] if 'common_arguments' in test_set_config['user_sync'] else None
        user_sync_path = test_set_config['user_sync']['user_sync_path']
        if re.match(r"^.*\.pex$", user_sync_path, re.IGNORECASE):
            user_sync_common_args = user_sync_path if not user_sync_common_args else "\"%s\" %s" % (user_sync_path, user_sync_common_args)
            user_sync_path = "python"

        self.test_suite_config = config
        self.test_suite_config.update({
            'user_sync_path': user_sync_path,
            'user_sync_common_args': user_sync_common_args
        })

        self.test_server_config = {
            'live_mode': config['live_mode'],
            'proxy_host': test_set_config['umapi']['proxy_host'],
            'destination_host': test_set_config['umapi']['destination_host']
        }

        test_group_name = self.test_suite_config['test_group_name']
        if test_group_name:
            if not os.path.isdir(os.path.join(test_suite_path,test_group_name)):
                raise error.AssertionException('test group "%s" not found.' % (test_group_name))
            self.test_group_names = [test_group_name]
        else:
            self.test_group_names = [f for f in os.listdir(test_suite_path) if os.path.isdir(os.path.join(test_suite_path, f))]

    def run(self):
        '''
        Runs the selected test groups in the test suite.
        '''
        for test_group_name in self.test_group_names:
            self.logger.info('Running test group "%s"...' % (test_group_name))
            test_group_path = os.path.join(self.test_suite_path, test_group_name)
            test_group = TestGroup(test_group_path, self.test_suite_config, self.test_server_config)
            test_group.run()


class TestGroup:
    def __init__(self, test_group_path, test_suite_config, test_server_config):
        '''
        Manages a test group, which is basically a directory in the same path as the suite configuration file.
        :type config_filename: str
        '''
        self.logger = logging.getLogger('test-group')
        self.test_group_path = test_group_path
        self.test_suite_config = test_suite_config
        self.test_server_config = test_server_config

        test_name = self.test_suite_config['test_name']
        if test_name:
            if not (os.path.isfile(os.path.join(test_group_path,test_name,TEST_CONFIG_FILENAME))):
                raise error.AssertionException('test-config.yml not found for test %s.' % (test_name))
            self.test_names = [test_name]
        else:
            self.test_names = [f for f in os.listdir(test_group_path) if os.path.isfile(os.path.join(test_group_path, f, TEST_CONFIG_FILENAME))]

    def run(self):
        '''
        Runs the selected tests in the test group.
        '''
        for test_name in self.test_names:
            self.logger.info('running test "%s"...' % (test_name))

            test_path = os.path.join(self.test_group_path, test_name)
            test = Test(test_path, self.test_suite_config, self.test_server_config)
            if self.test_suite_config['live_mode']:
                test.run_live()
            else:
                test.run()


class Test:
    def __init__(self, config_path, test_set_config, server_config):
        '''
        Sets up a user sync test, given a path to the test's configuration file.
        :type config_path: str
        '''
        config = ConfigFileLoader.load_from_yaml(os.path.join(config_path, 'test-config.yml'), TEST_TEMPLATE_KEYS)

        self.server_config = server_config
        self.server_config.update({
            'test_folder_path': config_path,
            'cassette_filename': config['server']['cassette_filename'],
        })

        self.test_config = test_set_config.copy()
        self.test_config.update({
            'config_path': config_path,
            'user_sync_args': config['user_sync']['arguments'],
            'live_working_dir': config['user_sync']['live']['working_dir'],
            'live_output_dir': config['user_sync']['live']['output_dir'],
            'test_working_dir': config['user_sync']['test']['working_dir'],
            'test_output_dir': config['user_sync']['test']['output_dir'],
        })

        self.logger = logging.getLogger('test')
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

    def _run(self, args, working_dir, output_filename, request_json_builder = None, live_request_json_builder = None):
        '''
        Runs the test given the command line arguments, and the output filename.
        :type args: list(str) representing the components of the command line argument.
        :c output_filename: str represents the filename of the file to write the command line output to.
        '''
        self.logger.info("%s" % (' '.join(args)))
        self._reset_output_file(output_filename)

        record_mode = 'all' if self.server_config['live_mode'] else 'none'
        recorder = vcr.VCR(
            record_mode=record_mode,
            match_on=('method', 'scheme', 'host', 'port', 'path', 'query'),
            decode_compressed_response=True
        )

        with recorder.use_cassette(self.server_config['cassette_filename']) as cassette:
            service = server.TestService(self.server_config, cassette, request_json_builder)
            service.run()

            with open(output_filename, 'w') as output_file:
                subprocess.call(args, cwd=working_dir, stdout=output_file, stderr=output_file, shell=IS_NT_PLATFORM)

            service.stop()

            if live_request_json_builder:
                for stored_request, stored_response in cassette.data:
                    if stored_request.body:
                        live_request_json_builder.extend_with_json_string(stored_request.body)

    def _compare_output(self, output_filename, live_output_filename):
        '''
        Compares the contents of the specified output filenames. The comparison is made by first stripping out the log
        entry timestamp, as well as certain string occurances, such as timestamps within the entry body, the actionID,
        and characters enclosed in double square brackets. Both the output file as well as the recorded output file are
        processed in this manner, then both have their lines sorted, then a line by line comparison is made. If a
        mismatch is found, an error is thrown detailing the two output lines and their respective line numbers.
        :type output_filename: str
        :type live_output_filename: str
        '''
        # log format defined in app.py (date, time, pid)
        timestamp_re = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \d+'

        LINE_TRANSFORM_MAP = [
            helper.StringTransformer(
                r"^%s (.*)\[\[.*\]\](.*)$" % (timestamp_re),
                r"%s\[\[\]\]%s"
            ),
            helper.StringTransformer(
                r"^%s (.*)requestID: action_\d+(.*)'requestID': 'action_\d+'(.*)$" % (timestamp_re),
                r"%srequestID: action_%s'requestID': 'action_'%s"
            ),
            helper.StringTransformer(
                r"^%s (.*\(Total time: )\d:\d\d:\d\d(\).*)$" % (timestamp_re),
                r"%s%s"
            ),
            helper.StringTransformer(
                r"^%s (.*)$" % (timestamp_re),
                r"%s"
            ),
        ]

        if not os.path.isfile(output_filename):
            raise error.AssertionException('OUTPUT COMPARE ERROR: Output file "%s" not found.' % (output_filename))
        if not os.path.isfile(live_output_filename):
            raise error.AssertionException('OUTPUT COMPARE ERROR: Recorded output file "%s" not found.'% (live_output_filename))

        with open(output_filename, 'r') as file:
            lines = file.read().splitlines()
        with open(live_output_filename, 'r') as rfile:
            lines_rec = rfile.read().splitlines()

        def transform_lines(lines):
            '''
            Transforms the specified list of strings to a a list of strings in which each string is passed through the
            transform map.
            :param lines: list(str)
            :return: list(str)
            '''
            lines_out = []
            for line in lines:
                for transform in LINE_TRANSFORM_MAP:
                    line_out = transform.transform(line)
                    if line_out is not None:
                        break
                lines_out.append(line_out if lines_out is not None else line)
            return lines_out

        def compare_line_tuple(line_tuple1, line_tuple2):
            index1, line1 = line_tuple1
            index2, line2 = line_tuple2
            return 1 if line1 > line2 else -1 if line1 < line2 else 0

        lines = transform_lines(lines)
        lines = zip(range(0, len(lines)), lines)
        lines.sort(compare_line_tuple)
        lines_rec = transform_lines(lines_rec)
        lines_rec = zip(range(0, len(lines_rec)), lines_rec)
        lines_rec.sort(compare_line_tuple)

        for line_tuple1, line_tuple2 in zip(lines, lines_rec):
            if not compare_line_tuple(line_tuple1, line_tuple2)==0:
                index1, line1 = line_tuple1
                index2, line2 = line_tuple2
                raise AssertionError('OUTPUT COMPARE ERROR: Output line mismatch\nOUTPUT (line %d):\n%s\nRECORDED OUTPUT (line %d):\n%s' % (index1, line1, index2, line2))

        if not len(lines) == len(lines_rec):
            raise error.AssertionException('OUTPUT COMPARE ERROR: Expected %d output lines, got %d lines.' % (len(lines_rec), len(lines)))


    def _compare_request_jsons(self, request_jsons, live_request_jsons):
        for request_json, live_request_json in zip(request_jsons, live_request_jsons):
            if not helper.deep_compare(request_json, live_request_json) == 0:
                raise AssertionError("Failed to match request json\n\nJSON ENTRY:%s\n\nRECORDED JSON ENTRY:%s" % (request_json, live_request_json))

        if not len(request_jsons) == len(live_request_jsons):
            raise AssertionError("Number of request JSON's do not match the pre-recorded number")

    def run_live(self):
        '''
        Runs the test in live mode. It first removes the existing recorded data, then runs the user-sync test service
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
            helper.JobStats.inc_test_success_count()
        except error.AssertionException as e:
            helper.JobStats.inc_test_fail_count()
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
            self._reset_output_file(self.test_config['test_output_dir'])

            args = [self.test_config['user_sync_path']]
            if self.test_config['user_sync_common_args']:
                args.extend(shlex.split(self.test_config['user_sync_common_args'], posix=not IS_NT_PLATFORM))
            args.extend(['--bypass-authentication-mode'])
            args.extend(shlex.split(self.test_config['user_sync_args'], posix=not IS_NT_PLATFORM))

            test_request_json_builder = helper.JSONBuilder()
            live_request_json_builder = helper.JSONBuilder()

            live_output_filename = os.path.join(self.test_config['live_output_dir'], 'out.txt')
            output_filename = os.path.join(self.test_config['test_output_dir'], 'out.txt')
            self._run(args, self.test_config['test_working_dir'], output_filename, test_request_json_builder, live_request_json_builder)
            self._compare_output(output_filename, live_output_filename)

            test_request_json = test_request_json_builder.json_val
            test_request_json.sort(helper.deep_compare)
            live_request_json = live_request_json_builder.json_val
            live_request_json.sort(helper.deep_compare)
            self._compare_request_jsons(test_request_json, live_request_json)

            self.logger.info('successfully ran and verified output for %s' % (self.test_config['config_path']))
            helper.JobStats.inc_test_success_count()
        except error.AssertionException as e:
            helper.JobStats.inc_test_fail_count()
            if not e.is_reported():
                self.logger.error('user-sync test error: %s' % (e.message))
                e.set_reported()

