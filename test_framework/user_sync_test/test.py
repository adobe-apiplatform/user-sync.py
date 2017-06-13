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
import subprocess
import server
import error
import shlex
import shutil
import config
import re
import logging
import vcr

import helper

IS_NT_PLATFORM = os.name == 'nt'

TEST_SUITE_TEMPLATE_KEYS = {
    '/user_sync/user_sync_path': (True, not IS_NT_PLATFORM, "../../dist/user-sync"),
    '/user_sync/user_sync_path_win': (True, IS_NT_PLATFORM, "../../dist/user-sync.pex"),
    '/umapi/users_request_matcher': (False, False, "https://usermanagement.adobe.io/v2/usermanagement/users/(.*)"),
    '/umapi/actions_request_matcher': (False, False, "https://usermanagement.adobe.io/v2/usermanagement/action/(.*)"),
}

TEST_GROUP_TEMPLATE_KEYS = {
    '/disabled': (False, False, False)
}

TEST_TEMPLATE_KEYS = {
    '/disabled': (False, False, False),
    '/user_sync/live/working_dir': (True, False, "live"),
    '/user_sync/live/output_dir': (True, False, "live/out"),
    '/user_sync/test/working_dir': (True, False, "test"),
    '/user_sync/test/output_dir': (True, False, "test/out"),
    '/server/cassette_filename': (True, False, 'live/cassette.yml'),
    '/verification/configuration_output/temp_path': (True, False, None),
    '/verification/configuration_output/temp_freeze_path': (False, False, None),
    '/verification/text_files': (False, False, []),
    '/verification/text_files/*': (True, True, None),
    '/verification/unordered_text_files': (False, False, []),
    '/verification/unordered_text_files/*': (True, True, None),
    '/verification/filtered_log_files': (False, False, []),
    '/verification/filtered_log_files/*': (False, False, None),
    }

TEST_GROUP_CONFIG_FILENAME = 'test-group-config.yml'
TEST_CONFIG_FILENAME = 'test-config.yml'

REQUEST_JSON_IGNORE_PATHS = set(
    '/do/requestID'
)

# log format defined in app.py (date, time, pid)
TIMESTAMP_RE = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \d+'
LINE_TRANSFORM_MAP = [
    helper.StringTransformer(
        r"^%s (.*)\[\[.*\]\](.*)$" % (TIMESTAMP_RE),
        r"%s\[\[\]\]%s"
    ),
    helper.StringTransformer(
        r"^%s (.*)requestID: action_\d+(.*)'requestID': 'action_\d+'(.*)$" % (TIMESTAMP_RE),
        r"%srequestID: action_%s'requestID': 'action_'%s"
    ),
    helper.StringTransformer(
        r"^%s (.*\(Total time: )\d:\d\d:\d\d(\).*)$" % (TIMESTAMP_RE),
        r"%s%s"
    ),
    helper.StringTransformer(
        r"^%s (.*)$" % (TIMESTAMP_RE),
        r"%s"
    ),
]


class TestSuite:
    def __init__(self, config_filename, app_config):
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
        test_suite_config = config.ConfigFileLoader.load_from_yaml(config_filename, TEST_SUITE_TEMPLATE_KEYS)
        self.test_suite_path = test_suite_path = os.path.dirname(config_filename)

        user_sync_common_args = test_suite_config['user_sync']['common_arguments'] if 'common_arguments' in test_suite_config['user_sync'] else None
        if IS_NT_PLATFORM:
            user_sync_path = test_suite_config['user_sync']['user_sync_path_win']
            user_sync_common_args = user_sync_path if not user_sync_common_args else "\"%s\" %s" % (user_sync_path, user_sync_common_args)
            user_sync_path = "python"
        else:
            user_sync_path = test_suite_config['user_sync']['user_sync_path']

        self.test_suite_config = app_config
        self.test_suite_config.update({
            'user_sync_path': user_sync_path,
            'user_sync_common_args': user_sync_common_args,
            'users_request_matcher': test_suite_config['umapi']['users_request_matcher'],
            'actions_request_matcher': test_suite_config['umapi']['actions_request_matcher']
        })

        self.test_server_config = {
            'live_mode': app_config['live_mode'],
            'proxy_host': test_suite_config['umapi']['proxy_host'],
            'destination_host': test_suite_config['umapi']['destination_host']
        }

        test_group_name = self.test_suite_config['test_group_name']
        if test_group_name:
            if not os.path.isdir(os.path.join(test_suite_path,test_group_name)):
                raise error.AssertionException('test group "%s" not found.' % (test_group_name))
            self.test_group_names = [test_group_name]
        else:
            self.test_group_names = [f for f in os.listdir(test_suite_path) if os.path.isfile(os.path.join(test_suite_path, f, TEST_GROUP_CONFIG_FILENAME))]

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
        test_group_config = config.ConfigFileLoader.load_from_yaml(os.path.join(test_group_path, TEST_GROUP_CONFIG_FILENAME), TEST_GROUP_TEMPLATE_KEYS)

        self.logger = logging.getLogger('test-group')
        self.test_group_disabled = test_group_config['disabled']
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
            test_path = os.path.join(self.test_group_path, test_name)
            test = Test(test_path, self.test_suite_config, self.test_server_config)
            if self.test_group_disabled or test.disabled:
                self.logger.info('test "%s" disabled.' % (test_name))
                helper.JobStats.inc_test_skip_count()
            else:
                self.logger.info('running test "%s"...' % (test_name))
                if self.test_suite_config['live_mode']:
                    test.run_live()
                else:
                    test.run()


class Test:
    def __init__(self, config_path, test_suite_config, server_config):
        '''
        Sets up a user sync test, given a path to the test's configuration file.
        :type config_path: str
        '''
        test_config = config.ConfigFileLoader.load_from_yaml(os.path.join(config_path, 'test-config.yml'), TEST_TEMPLATE_KEYS)

        self.server_config = server_config
        self.server_config.update({
            'test_folder_path': config_path,
            'cassette_filename': test_config['server']['cassette_filename'],
        })

        self.test_suite_config = test_suite_config.copy()
        self.config_path = config_path
        self.disabled = test_config['disabled']
        self.user_sync_args = test_config['user_sync']['arguments']
        self.live_working_dir = test_config['user_sync']['live']['working_dir']
        self.live_output_dir = test_config['user_sync']['live']['output_dir']
        self.test_working_dir = test_config['user_sync']['test']['working_dir']
        self.test_output_dir = test_config['user_sync']['test']['output_dir']
        self.verification_text_files = test_config['verification']['text_files']
        self.verification_unordered_text_files = test_config['verification']['unordered_text_files']
        self.verification_filtered_log_files = test_config['verification']['filtered_log_files']
        self.temp_path = test_config['verification']['configuration_output']['temp_path']
        self.temp_freeze_path = test_config['verification']['configuration_output']['temp_freeze_path']

        self.temp_freeze = self.temp_path is not None and self.temp_freeze_path is not None

        if self.user_sync_args is None:
            self.user_sync_args = ""

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

    def _copy_dir(self,srcpath,dstpath):
        '''
        Duplicates the specified directory into the destination folder.
        :type filename: str
        '''
        if not os.path.isdir(srcpath):
            raise error.AssertionException("specified path is not a folder")

        shutil.copytree(srcpath,dstpath)

    def _run(self, args, working_dir, output_filename, request_json_builder = None, live_request_json_builder = None):
        '''
        Runs the test given the command line arguments, and the output filename.
        :type args: list(str) representing the components of the command line argument.
        :c output_filename: str represents the filename of the file to write the command line output to.
        '''
        self.logger.info("%s" % (' '.join(args)))
        self._reset_output_file(output_filename)

        def match_um_requests_on(r1, r2):
            '''
            Custom uri matcher for use with vcrpy. Basically it provides custom matching for user and action UM
            requests, which ignores the org ID portion of the request. Otherwise, the request uri must match exactly.
            :param r1: 
            :param r2: 
            :return: 
            '''
            if re.match(self.test_suite_config['users_request_matcher'], r1.uri):
                if re.match(self.test_suite_config['users_request_matcher'], r2.uri):
                    return True

            if re.match(self.test_suite_config['actions_request_matcher'], r2.uri):
                if re.match(self.test_suite_config['actions_request_matcher'], r2.uri):
                    return True

            return r1.uri == r2.uri

        record_mode = 'all' if self.server_config['live_mode'] else 'none'
        recorder = vcr.VCR(
            record_mode=record_mode,
            match_on=['um_request'],
            # match_on=match_um_requests_on,
            decode_compressed_response=True,
            filter_headers=['authorization']
        )
        recorder.register_matcher('um_request',match_um_requests_on)

        with recorder.use_cassette(self.server_config['cassette_filename']) as cassette:
            service = server.TestService(self.server_config, cassette, request_json_builder)
            service.run()

            with open(output_filename, 'w') as output_file:
                subprocess.call(args, cwd=working_dir, stdin=None, stdout=output_file, stderr=output_file, shell=IS_NT_PLATFORM)
                # p = subprocess.Popen(args, cwd=working_dir, stdout=output_file, stderr=output_file)
                # output_bytes = subprocess.check_output(cmd, cwd=working_dir, shell=True)
                # output_file.write(output_bytes.decode())
                # p.communicate()

            service.stop()

            if live_request_json_builder:
                for stored_request, stored_response in cassette.data:
                    if stored_request.body:
                        live_request_json_builder.extend_with_json_string(stored_request.body)

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
            self._reset_output_file(self.live_output_dir)
            if self.temp_freeze:
                temp_freeze_path = os.path.join(self.live_output_dir, self.temp_freeze_path)
                self._reset_output_file(self.temp_path)
                self._reset_output_file(temp_freeze_path)

            args = [self.test_suite_config['user_sync_path']]
            if self.test_suite_config['user_sync_common_args']:
                args.extend(shlex.split(self.test_suite_config['user_sync_common_args'], posix=not IS_NT_PLATFORM))
                # args.extend(shlex.split(self.test_suite_config['user_sync_common_args']))
            args.extend(['--test-framework','live'])
            # args.extend(shlex.split(self.user_sync_args, posix=not IS_NT_PLATFORM))
            args.extend(shlex.split(self.user_sync_args, posix=not IS_NT_PLATFORM))

            output_filename = os.path.join(self.live_output_dir, 'out.txt')
            self._run(args, self.live_working_dir, output_filename)

            if self.temp_freeze:
                self._copy_dir(self.temp_path, temp_freeze_path)

            self.logger.info('successfully recorded %s' % (self.config_path))
            helper.JobStats.inc_test_success_count()
        except error.AssertionException as e:
            helper.JobStats.inc_test_fail_count()
            if not e.is_reported():
                self.logger.error('user-sync test error: %s' % (e.message))
                e.set_reported()

    def run(self):
        '''
        Runs the test using canned data. This simply sets the user-sync test service to use the recorded data, instead
        of connecting to the live Adobe server, and launches the user-sync tool with --test-framework. Then
        test ends by saving the user-sync tool output to the configured path.
        '''
        try:
            self._reset_output_file(self.test_output_dir)
            if self.temp_freeze:
                temp_freeze_path = os.path.join(self.test_output_dir, self.temp_freeze_path)
                self._reset_output_file(self.temp_path)
                self._reset_output_file(temp_freeze_path)

            args = [self.test_suite_config['user_sync_path']]
            if self.test_suite_config['user_sync_common_args']:
                args.extend(shlex.split(self.test_suite_config['user_sync_common_args'], posix=not IS_NT_PLATFORM))
            args.extend(['--test-framework','test'])
            args.extend(shlex.split(self.user_sync_args, posix=not IS_NT_PLATFORM))

            test_request_json_builder = helper.JSONBuilder()
            live_request_json_builder = helper.JSONBuilder()

            live_output_filename = os.path.join(self.live_output_dir, 'out.txt')
            output_filename = os.path.join(self.test_output_dir, 'out.txt')
            self._run(args, self.test_working_dir, output_filename, test_request_json_builder, live_request_json_builder)

            if self.temp_freeze:
                self._copy_dir(self.temp_path, temp_freeze_path)

            helper.verify_unordered_text_files(output_filename, live_output_filename, LINE_TRANSFORM_MAP)

            # smart match umapi requests
            test_request_json = test_request_json_builder.json_val
            test_request_json.sort(helper.deep_compare)
            live_request_json = live_request_json_builder.json_val
            live_request_json.sort(helper.deep_compare)
            self._compare_request_jsons(test_request_json, live_request_json)

            # compare files indicated by user for verification
            for text_file in self.verification_text_files:
                live_text_filename = os.path.join(self.live_output_dir,text_file)
                test_text_filename = os.path.join(self.test_output_dir,text_file)
                helper.verify_text_files(live_text_filename, test_text_filename)

            # compare file indicated by user with unordered text lines for verification
            for text_file in self.verification_unordered_text_files:
                live_text_filename = os.path.join(self.live_output_dir,text_file)
                test_text_filename = os.path.join(self.test_output_dir,text_file)
                helper.verify_unordered_text_files(live_text_filename, test_text_filename)

            def find_matching_file(dirpath, filename_re):
                filename = None
                for r,d,f in os.walk(dirpath):
                    for file in f:
                        if re.match(filename_re, file):
                            if filename is not None:
                                raise error.VerificationException('multiple files match verification file expression "%s"' % (filename_re))
                            filename = os.path.join(r,file)
                if filename is None:
                    raise error.VerificationException('No files match verification file expression "%s"' % (filename_re))
                return filename

            for log_filename_re in self.verification_filtered_log_files:
                live_log_filename = find_matching_file(self.live_output_dir, log_filename_re)
                test_log_filename = find_matching_file(self.test_output_dir, log_filename_re)
                helper.verify_unordered_text_files(test_log_filename, live_log_filename, LINE_TRANSFORM_MAP)

            self.logger.info('successfully ran and verified output for %s' % (self.config_path))
            helper.JobStats.inc_test_success_count()
        except error.VerificationException as e:
            helper.JobStats.inc_test_fail_count()
            if not e.is_reported():
                self.logger.error('OUTPUT VERIFICATION ERROR: %s' % (e.message))
                e.set_reported()
        except error.AssertionException as e:
            helper.JobStats.inc_test_fail_count()
            if not e.is_reported():
                self.logger.error(e.message)
                e.set_reported()

