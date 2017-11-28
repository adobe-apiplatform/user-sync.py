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

import argparse
import logging
import os
import re
import sys
from datetime import datetime

import six

import user_sync.config
import user_sync.connector.directory
import user_sync.connector.umapi
import user_sync.helper
import user_sync.lockfile
import user_sync.rules
from user_sync.error import AssertionException
from user_sync.version import __version__ as APP_VERSION

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# file global logger, defined early so later functions can refer to it.
logger = logging.getLogger('main')


def init_console_log():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    return handler

# file global console_log_handler, defined early so later functions can refer to it.
console_log_handler = init_console_log()


def process_args():
    parser = argparse.ArgumentParser(description='User Sync from Adobe')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + APP_VERSION)
    parser.add_argument('-t', '--test-mode',
                        help='run API action calls in test mode (does not execute changes on the Adobe side). Logs '
                             'what would have been executed.',
                        action='store_true', dest='test_mode')
    parser.add_argument('-c', '--config-filename',
                        help='main config filename. (default: "%(default)s")',
                        default=user_sync.config.DEFAULT_MAIN_CONFIG_FILENAME,
                        metavar='filename', dest='config_filename')
    parser.add_argument('--users',
                        help="specify the users to be considered for sync. Legal values are 'all' (the default), "
                             "'group names' (one or more specified groups), 'mapped' (all groups listed in "
                             "the configuration file), 'file f' (a specified input file).",
                        nargs="+", metavar=('all|file|mapped|group', 'arg1'), dest='users', default=['all'])
    parser.add_argument('--user-filter',
                        help='limit the selected set of users that may be examined for syncing, with the pattern '
                             'being a regular expression.',
                        metavar='pattern', dest='username_filter_pattern')
    parser.add_argument('--update-user-info',
                        help='if user information differs between the enterprise side and the Adobe side, the Adobe '
                             'side is updated to match.',
                        action='store_true', dest='update_user_info')
    parser.add_argument('--process-groups',
                        help='if membership in mapped groups differs between the enterprise directory and Adobe sides, '
                             'the group membership is updated on the Adobe side so that the memberships in mapped '
                             'groups match those on the enterprise directory side.',
                        action='store_true', dest='manage_groups')
    parser.add_argument('--adobe-only-user-action',
                        help="specify what action to take on Adobe users that don't match users from the "
                             "directory.  Options are 'exclude' (from all changes), "
                             "'preserve' (as is except for --process-groups, the default), "
                             "'write-file f' (preserve and list them), "
                             "'remove-adobe-groups' (but do not remove users)"
                             "'remove' (users but preserve cloud storage), "
                             "'delete' (users and their cloud storage), ",
                        nargs="*", metavar=('exclude|preserve|write-file|delete|remove|remove-adobe-groups', 'arg1'),
                        dest='adobe_only_user_action')
    parser.add_argument('--adobe-only-user-list',
                        help="instead of computing Adobe-only users (Adobe users with no matching users "
                             "in the directory) by comparing Adobe users with directory users, "
                             "the list is read from a file (see --adobe-only-user-action write-file). "
                             "When using this option, you must also specify what you want done with Adobe-only "
                             "users by also including --adobe-only-user-action and one of its arguments",
                        metavar='input_path', dest='stray_list_input_path')
    parser.add_argument('--config-file-encoding',
                        help="configuration files are expected to be utf8-encoded (which includes ascii); if you "
                             "use a different character set, then specify it with this argument. "
                             "All encoding names understood by Python are allowed.",
                        dest='encoding_name', default='utf8')
    parser.add_argument('--strategy',
                        help="whether to fetch and sync the Adobe directory against the customer directory "
                             "or just to push each customer user to the Adobe side.  Default is to fetch and sync.",
                        dest='strategy', metavar='sync|push', default='sync')
    parser.add_argument('--connector',
                        help='specify a connector to use; default is LDAP (or CSV if --users file is specified)',
                        nargs='+', metavar=['ldap|okta|csv','path-to-file.csv'],
                        dest='connector_spec', default=['ldap'])
    return parser.parse_args()


def init_log(logging_config):
    """
    :type logging_config: user_sync.config.DictConfig
    """
    builder = user_sync.config.OptionsBuilder(logging_config)
    builder.set_bool_value('log_to_file', False)
    builder.set_string_value('file_log_directory', 'logs')
    builder.set_string_value('file_log_name_format', '{:%Y-%m-%d}.log')
    builder.set_string_value('file_log_level', 'info')
    builder.set_string_value('console_log_level', 'info')
    options = builder.get_options()

    level_lookup = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    console_log_level = level_lookup.get(options['console_log_level'])
    if console_log_level is None:
        console_log_level = logging.INFO
        logger.log(logging.WARNING, 'Unknown console log level: %s setting to info' % options['console_log_level'])
    console_log_handler.setLevel(console_log_level)

    if options['log_to_file']:
        unknown_file_log_level = False
        file_log_level = level_lookup.get(options['file_log_level'])
        if file_log_level is None:
            file_log_level = logging.INFO
            unknown_file_log_level = True
        file_log_directory = options['file_log_directory']
        if not os.path.exists(file_log_directory):
            os.makedirs(file_log_directory)

        file_path = os.path.join(file_log_directory, options['file_log_name_format'].format(datetime.now()))
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))
        logging.getLogger().addHandler(file_handler)
        if unknown_file_log_level:
            logger.log(logging.WARNING, 'Unknown file log level: %s setting to info' % options['file_log_level'])


def begin_work(config_loader):
    """
    :type config_loader: user_sync.config.ConfigLoader
    """

    directory_groups = config_loader.get_directory_groups()
    primary_umapi_config, secondary_umapi_configs = config_loader.get_umapi_options()
    rule_config = config_loader.get_rule_options()

    # process mapped configuration after the directory groups have been loaded, as mapped setting depends on this.
    if rule_config['directory_group_mapped']:
        rule_config['directory_group_filter'] = set(six.iterkeys(directory_groups))

    # make sure that all the adobe groups are from known umapi connector names
    referenced_umapi_names = set()
    for groups in six.itervalues(directory_groups):
        for group in groups:
            umapi_name = group.umapi_name
            if umapi_name != user_sync.rules.PRIMARY_UMAPI_NAME:
                referenced_umapi_names.add(umapi_name)
    referenced_umapi_names.difference_update(six.iterkeys(secondary_umapi_configs))

    if len(referenced_umapi_names) > 0:
        raise AssertionException('Adobe groups reference unknown umapi connectors: %s' % referenced_umapi_names)

    directory_connector = None
    directory_connector_options = None
    directory_connector_module_name = config_loader.get_directory_connector_module_name()
    if directory_connector_module_name is not None:
        directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])
        directory_connector = user_sync.connector.directory.DirectoryConnector(directory_connector_module)
        directory_connector_options = config_loader.get_directory_connector_options(directory_connector.name)

    config_loader.check_unused_config_keys()

    if directory_connector is not None and directory_connector_options is not None:
        # specify the default user_identity_type if it's not already specified in the options
        if 'user_identity_type' not in directory_connector_options:
            directory_connector_options['user_identity_type'] = rule_config['new_account_type']
        directory_connector.initialize(directory_connector_options)

    primary_name = '.primary' if secondary_umapi_configs else ''
    umapi_primary_connector = user_sync.connector.umapi.UmapiConnector(primary_name, primary_umapi_config)
    umapi_other_connectors = {}
    for secondary_umapi_name, secondary_config in six.iteritems(secondary_umapi_configs):
        umapi_secondary_conector = user_sync.connector.umapi.UmapiConnector(".secondary.%s" % secondary_umapi_name,
                                                                            secondary_config)
        umapi_other_connectors[secondary_umapi_name] = umapi_secondary_conector
    umapi_connectors = user_sync.rules.UmapiConnectors(umapi_primary_connector, umapi_other_connectors)

    rule_processor = user_sync.rules.RuleProcessor(rule_config)
    if len(directory_groups) == 0 and rule_processor.will_manage_groups():
        logger.warning('No group mapping specified in configuration but --process-groups requested on command line')
    rule_processor.run(directory_groups, directory_connector, umapi_connectors)


def create_config_loader(args):
    config_bootstrap_options = {
        'main_config_filename': args.config_filename,
        'config_file_encoding': args.encoding_name,
    }
    config_loader = user_sync.config.ConfigLoader(config_bootstrap_options)
    return config_loader


def create_config_loader_options(args):
    """
    This is where all the command-line arguments get set as options in the main config
    so that it appears as if they were loaded as part of the main configuration file.
    If you add an option that is supposed to be set from the command line here, you
    had better make sure you add it to the ones read in get_rule_options.
    :param args: the command-line args as parsed
    :return: the configured options for the config loader.
    """
    config_options = {
        'delete_strays': False,
        'directory_connector_overridden_options': None,
        'directory_connector_type': None,
        'directory_group_filter': None,
        'directory_group_mapped': False,
        'disentitle_strays': False,
        'exclude_strays': False,
        'manage_groups': args.manage_groups,
        'remove_strays': False,
        'strategy': 'sync',
        'stray_list_input_path': None,
        'stray_list_output_path': None,
        'test_mode': args.test_mode,
        'update_user_info': args.update_user_info,
        'username_filter_regex': None,
    }

    # --connector
    connector_type = user_sync.helper.normalize_string(args.connector_spec.pop(0))
    if connector_type in ["ldap", "okta"]:
        if args.connector_spec:
            raise AssertionException("Must not specify file (%s) with --connector %s" %
                                     (args.connector_spec[0], connector_type))
        config_options['directory_connector_type'] = connector_type
    elif connector_type == "csv":
        if len(args.connector_spec) != 1:
            raise AssertionException("Must specify a single file with CSV connector")
        config_options['directory_connector_type'] = 'csv'
        config_options['directory_connector_overridden_options'] = {'file_path': args.connector_spec.pop(0)}
    else:
        raise AssertionException("Unknown connector type: %s" % connector_type)

    # --users
    users_args = args.users
    users_action = None if not users_args else user_sync.helper.normalize_string(users_args.pop(0))
    if users_action is None or users_action == 'all':
        if config_options['directory_connector_type'] == 'okta':
            raise AssertionException('Okta connector module does not support "--users all"')
    elif users_action == 'file':
        if config_options['directory_connector_type'] == 'csv':
            raise AssertionException('You cannot specify "--users file" and "--connector csv file"')
        if len(users_args) == 0:
            raise AssertionException('Missing file path for --users %s [file_path]' % users_action)
        config_options['directory_connector_type'] = 'csv'
        config_options['directory_connector_overridden_options'] = {'file_path': users_args.pop(0)}
    elif users_action == 'mapped':
        config_options['directory_group_mapped'] = True
    elif users_action == 'group':
        if len(users_args) == 0:
            raise AssertionException('Missing groups for --users %s [groups]' % users_action)
        config_options['directory_group_filter'] = users_args.pop(0).split(',')
    else:
        raise AssertionException('Unknown argument --users %s' % users_action)

    username_filter_pattern = args.username_filter_pattern
    if username_filter_pattern:
        try:
            compiled_expression = re.compile(r'\A' + username_filter_pattern + r'\Z', re.IGNORECASE)
        except Exception as e:
            raise AssertionException("Bad regular expression for --user-filter: %s reason: %s" %
                                     (username_filter_pattern, e))
        config_options['username_filter_regex'] = compiled_expression

    # --adobe-only-user-action
    adobe_action_args = args.adobe_only_user_action
    if adobe_action_args is not None:
        adobe_action = None if not adobe_action_args else user_sync.helper.normalize_string(adobe_action_args.pop(0))
        if adobe_action is None or adobe_action == 'preserve':
            pass  # no option settings needed
        elif adobe_action == 'exclude':
            config_options['exclude_strays'] = True
        elif adobe_action == 'write-file':
            if not adobe_action_args:
                raise AssertionException('Missing file path for --adobe-only-user-action %s [file_path]' % adobe_action)
            config_options['stray_list_output_path'] = adobe_action_args.pop(0)
        elif adobe_action == 'delete':
            config_options['delete_strays'] = True
        elif adobe_action == 'remove':
            config_options['remove_strays'] = True
        elif adobe_action == 'remove-adobe-groups':
            config_options['disentitle_strays'] = True
        else:
            raise AssertionException('Unknown argument --adobe-only-user-action %s' % adobe_action)

    # --adobe-only-user-list
    stray_list_input_path = args.stray_list_input_path
    if stray_list_input_path:
        if users_args is not None:
            raise AssertionException('You cannot specify both --users and --adobe-only-user-list')
        if config_options.get('stray_list_output_path'):
            raise AssertionException('You cannot specify both --adobe-only-user-list and --output-adobe-users')
        # don't read the directory when processing from the stray list
        config_options['directory_connector_type'] = None
        logger.info('--adobe-only-user-list specified, so not reading or comparing directory and Adobe users')
        config_options['stray_list_input_path'] = stray_list_input_path

    # --strategy
    if user_sync.helper.normalize_string(args.strategy) == 'push':
        config_options['strategy'] = 'push'
        if stray_list_input_path or adobe_action_args is not None:
            raise AssertionException("You cannot specify '--strategy push' and any '--adobe-only-user' options")

    return config_options


def log_parameters(args):
    """
    Log the invocation parameters to make it easier to diagnose problem with customers
    :param args: namespace
    :return: None
    """
    logger.info('------- Invocation parameters -------')
    logger.info(' '.join(sys.argv))
    logger.debug('-------- Internal parameters --------')
    for parameter_name, parameter_value in six.iteritems(args.__dict__):
        logger.debug('  %s: %s', parameter_name, parameter_value)
    logger.info('-------------------------------------')


def main():
    run_stats = None
    try:
        try:
            args = process_args()
        except SystemExit:
            return

        config_loader = create_config_loader(args)
        init_log(config_loader.get_logging_config())

        # add start divider, app version number, and invocation parameters to log
        run_stats = user_sync.helper.JobStats('Run (User Sync version: ' + APP_VERSION + ')', divider='=')
        run_stats.log_start(logger)
        log_parameters(args)

        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        lock_path = os.path.join(script_dir, 'lockfile')
        lock = user_sync.lockfile.ProcessLock(lock_path)
        if lock.set_lock():
            try:
                config_options = create_config_loader_options(args)
                config_loader.set_options(config_options)

                begin_work(config_loader)
            finally:
                lock.unlock()
        else:
            logger.critical("A different User Sync process is currently running.")

    except AssertionException as e:
        if not e.is_reported():
            logger.critical("%s", e)
            e.set_reported()
    except KeyboardInterrupt:
        try:
            logger.critical('Keyboard interrupt, exiting immediately.')
        except:
            pass
    except:
        try:
            logger.error('Unhandled exception', exc_info=sys.exc_info())
        except:
            pass

    finally:
        if run_stats is not None:
            run_stats.log_end(logger)


if __name__ == '__main__':
    main()
