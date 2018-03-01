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
from user_sync.version import __version__ as app_version

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# file logger, defined early so later functions can refer to it.
logger = logging.getLogger('main')


def init_console_log():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    return handler


# console logger, initialized early so there is at least one logger available.
console_log_handler = init_console_log()


def main(args=sys.argv[1:]):
    """Top level entry point.

    To invoke User Sync from your code in an embedded fashion,
    call this function, specifying the desired arguments.
    """
    run_stats = None
    try:
        try:
            arg_obj = process_args(args)
        except SystemExit:
            return

        # load the config files and start the file logger
        config_loader = user_sync.config.ConfigLoader(arg_obj)
        init_log(config_loader.get_logging_config())

        # add start divider, app version number, and invocation parameters to log
        run_stats = user_sync.helper.JobStats('Run (User Sync version: ' + app_version + ')', divider='=')
        run_stats.log_start(logger)
        log_parameters(args, config_loader)

        script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        lock_path = os.path.join(script_dir, 'lockfile')
        lock = user_sync.lockfile.ProcessLock(lock_path)
        if lock.set_lock():
            try:
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


def process_args(args=None):
    """Define and parse the command-line (or passed) args.

    All of the arg defaults are actually held in the config module or config files,
    and the command line is just used to override those, so we don't define defaults here.
    """
    # first define the standard args implemented by argparse ('-v', -h')
    parser = argparse.ArgumentParser(description='User Sync from Adobe')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + app_version)

    # next define the arguments that affect reading the configuration file
    # these are listed in alphabetical order!  always add new ones that way!
    parser.add_argument('--config-file-encoding',
                        help="encoding of your configuration files (default %s)".format(
                            user_sync.config.ConfigLoader.config_defaults['config_encoding']
                        ),
                        metavar='encoding-name',
                        dest='encoding_name')
    parser.add_argument('-c', '--config-filename',
                        help="path to your main configuration file (default %s)".format(
                            user_sync.config.ConfigLoader.config_defaults['config_filename']
                        ),
                        metavar='path-to-file',
                        dest='config_filename')

    # finally define the arguments that affect processing operations;
    # these are listed in alphabetical order!  always add new ones that way!
    parser.add_argument('--adobe-only-user-action',
                        help="specify what action to take on Adobe users that don't match users from the "
                             "directory.  Options are 'exclude' (from all changes), "
                             "'preserve' (as is except for --process-groups, the default), "
                             "'write-file f' (preserve and list them), "
                             "'remove-adobe-groups' (but do not remove users)"
                             "'remove' (users but preserve cloud storage), "
                             "'delete' (users and their cloud storage), ",
                        nargs="+",
                        metavar=('exclude|preserve|delete|remove|remove-adobe-groups|write-file', 'path-to-file.csv'),
                        dest='adobe_only_user_action')
    parser.add_argument('--adobe-only-user-list',
                        help="instead of computing Adobe-only users (Adobe users with no matching users "
                             "in the directory) by comparing Adobe users with directory users, "
                             "the list is read from a file (see --adobe-only-user-action write-file). "
                             "When using this option, you must also specify what you want done with Adobe-only "
                             "users by also including --adobe-only-user-action and one of its arguments",
                        metavar='input_path',
                        dest='adobe_only_user_list')
    parser.add_argument('--connector',
                        help='specify a connector to use; default is LDAP (or CSV if --users file is specified)',
                        nargs='+',
                        metavar=('ldap|okta|csv', 'path-to-file.csv'),
                        dest='connector')
    parser.add_argument('--process-groups',
                        help='if membership in mapped groups differs between the enterprise directory and Adobe sides, '
                             'the group membership is updated on the Adobe side so that the memberships in mapped '
                             'groups match those on the enterprise directory side.',
                        action='store_true',
                        dest='process_groups')
    parser.add_argument('--no-process-groups',
                        help='if membership in mapped groups differs between the enterprise directory and Adobe sides, '
                             'the group membership is updated on the Adobe side so that the memberships in mapped '
                             'groups match those on the enterprise directory side.',
                        action='store_false',
                        dest='process_groups')
    parser.add_argument('--strategy',
                        help="whether to fetch and sync the Adobe directory against the customer directory "
                             "or just to push each customer user to the Adobe side.  Default is to fetch and sync.",
                        metavar='sync|push',
                        dest='strategy')
    parser.add_argument('-t', '--test-mode',
                        help='enable test mode (API calls do not execute changes on the Adobe side).',
                        action='store_true',
                        dest='test_mode')
    parser.add_argument('-T', '--no-test-mode',
                        help='disable test mode (API calls execute changes on the Adobe side).',
                        action='store_false',
                        dest='test_mode')
    parser.add_argument('--user-filter',
                        help='limit the selected set of users that may be examined for syncing, with the pattern '
                             'being a regular expression.',
                        metavar='pattern',
                        dest='user_filter')
    parser.add_argument('--users',
                        help="specify the users to be considered for sync. Legal values are 'all' (the default), "
                             "'group names' (one or more specified groups), 'mapped' (all groups listed in "
                             "the configuration file), 'file f' (a specified input file).",
                        nargs="+",
                        metavar=('all|file|mapped|group', 'groups|path-to-file.csv'),
                        dest='users')
    parser.add_argument('--update-user-info',
                        help='user attributes on the Adobe side are updated from the directory.',
                        action='store_true',
                        dest='update_user_info')
    parser.add_argument('--no-update-user-info',
                        help='user attributes on the Adobe side are not updated from the directory.',
                        action='store_false',
                        dest='update_user_info')
    # make sure the boolean arguments have no default value
    parser.set_defaults(process_groups=None, test_mode=None, update_user_info=None)
    return parser.parse_args(args)


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


def log_parameters(argv, config_loader):
    """
    Log the invocation parameters to make it easier to diagnose problem with customers
    :param argv: command line arguments (a la sys.argv)
    :type argv: list(str)
    :param config_loader: the main configuration loader
    :type config_loader: user_sync.config.ConfigLoader
    :return: None
    """
    python_version = ' ' * 13 + 'Python %s.%s.%s' % sys.version_info[:3]
    logger.info('')
    logger.info(python_version)
    logger.info('------- Command line arguments -------')
    logger.info(' '.join(argv))
    logger.debug('-------- Resulting invocation options --------')
    for parameter_name, parameter_value in six.iteritems(config_loader.get_invocation_options()):
        logger.debug('  %s: %s', parameter_name, parameter_value)
    logger.info('-------------------------------------')


def begin_work(config_loader):
    """
    :type config_loader: user_sync.config.ConfigLoader
    """
    directory_groups = config_loader.get_directory_groups()
    rule_config = config_loader.get_rule_options()

    # make sure that all the adobe groups are from known umapi connector names
    primary_umapi_config, secondary_umapi_configs = config_loader.get_umapi_options()
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
    if len(directory_groups) == 0 and rule_processor.will_process_groups():
        logger.warning('No group mapping specified in configuration but --process-groups requested on command line')
    rule_processor.run(directory_groups, directory_connector, umapi_connectors)


if __name__ == '__main__':
    main()
