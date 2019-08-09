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

import argparse
import logging
import os
import sys
import click
import shutil
from click_default_group import DefaultGroup
from datetime import datetime

import six

import user_sync.config
import user_sync.connector.directory
import user_sync.connector.directory_ldap
import user_sync.connector.directory_okta
import user_sync.connector.directory_csv
import user_sync.connector.umapi
import user_sync.helper
import user_sync.lockfile
import user_sync.rules
import user_sync.cli
import user_sync.resource
import time

import user_sync.sign_sync.app as sign_sync

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


@click.group(cls=DefaultGroup, default='sync', default_if_no_args=True)
@click.help_option('-h', '--help')
@click.version_option(app_version, '-v', '--version', message='%(prog)s %(version)s')
def main():
    """User Sync from Adobe

    Full documentation:

    https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/

    NOTE: The defaults documented here can be overridden in `invocation_defaults` in
    `user-sync-config.yml`.  However, any options explicitly set on the command line will
    override any options set in `invocation_defaults`.

    COMMAND HELP:

    user-sync [COMMAND] -h/--help
    """
    pass


@main.command()
@click.help_option('-h', '--help')
@click.option('--config-file-encoding', 'encoding_name',
              help="encoding of your configuration files",
              type=str,
              nargs=1,
              metavar='encoding-name')
@click.option('-c', '--config-filename',
              help="path to your main configuration file",
              type=str,
              nargs=1,
              metavar='path-to-file')
@click.option('--adobe-only-user-action',
              help="specify what action to take on Adobe users that don't match users from the "
                   "directory.  Options are 'exclude' (from all changes), "
                   "'preserve' (as is except for --process-groups, the default), "
                   "'write-file f' (preserve and list them), "
                   "'remove-adobe-groups' (but do not remove users)"
                   "'remove' (users but preserve cloud storage), "
                   "'delete' (users and their cloud storage), ",
              cls=user_sync.cli.OptionMulti,
              type=list,
              metavar='exclude|preserve|delete|remove|remove-adobe-groups|write-file [path-to-file.csv]')
@click.option('--adobe-only-user-list',
              help="instead of computing Adobe-only users (Adobe users with no matching users "
                   "in the directory) by comparing Adobe users with directory users, "
                   "the list is read from a file (see --adobe-only-user-action write-file). "
                   "When using this option, you must also specify what you want done with Adobe-only "
                   "users by also including --adobe-only-user-action and one of its arguments",
              type=str,
              nargs=1,
              metavar='input_path')
@click.option('--adobe-users',
              help="specify the adobe users to pull from UMAPI. Legal values are 'all' (the default), "
                   "'group names' (one or more specified groups), 'mapped' (all groups listed in "
                   "the configuration file)",
              cls=user_sync.cli.OptionMulti,
              type=list,
              metavar='all|mapped|group [group list]')
@click.option('--connector',
              help='specify a connector to use; default is LDAP (or CSV if --users file is specified)',
              cls=user_sync.cli.OptionMulti,
              type=list,
              metavar='ldap|okta|csv|adobe_console [path-to-file.csv]')
@click.option('--exclude-unmapped-users/--include-unmapped-users', default=None,
              help='Exclude users that is not part of a mapped group from being created on Adobe side')
@click.option('--process-groups/--no-process-groups', default=None,
              help='if membership in mapped groups differs between the enterprise directory and Adobe sides, '
                   'the group membership is updated on the Adobe side so that the memberships in mapped '
                   'groups match those on the enterprise directory side.')
@click.option('--strategy',
              help="whether to fetch and sync the Adobe directory against the customer directory "
                   "or just to push each customer user to the Adobe side.  Default is to fetch and sync.",
              nargs=1,
              type=str,
              metavar='sync|push')
@click.option('-t/-T', '--test-mode/--no-test-mode', default=None,
              help='enable test mode (API calls do not execute changes on the Adobe side).')
@click.option('--user-filter',
              help='limit the selected set of users that may be examined for syncing, with the pattern '
                   'being a regular expression.',
              nargs=1,
              type=str,
              metavar='pattern')
@click.option('--users',
              help="specify the users to be considered for sync. Legal values are 'all' (the default), "
                   "'group names' (one or more specified groups), 'mapped' (all groups listed in "
                   "the configuration file), 'file f' (a specified input file).",
              cls=user_sync.cli.OptionMulti,
              type=list,
              metavar='all|file|mapped|group [group list or path-to-file.csv]')
@click.option('--update-user-info/--no-update-user-info', default=None,
              help='user attributes on the Adobe side are updated from the directory.')
def sync(**kwargs):
    """Run User Sync [default command]"""
    run_stats = None
    sign_config_file = kwargs.get('sign_sync_config')
    if 'sign_sync_config' in kwargs:
        del(kwargs['sign_sync_config'])
    try:
        # load the config files and start the file logger
        config_loader = user_sync.config.ConfigLoader(kwargs)
        init_log(config_loader.get_logging_config())

        # add start divider, app version number, and invocation parameters to log
        run_stats = user_sync.helper.JobStats('Run (User Sync version: ' + app_version + ')', divider='=')
        run_stats.log_start(logger)
        log_parameters(sys.argv[1:], config_loader)

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


@main.command()
@click.help_option('-h', '--help')
@click.option('--root', help="Filename of root user sync config file",
              prompt='Main Config Filename', default='user-sync-config.yml')
@click.option('--umapi', help="Filename of UMAPI credential config file",
              prompt='UMAPI Config Filename', default='connector-umapi.yml')
@click.option('--ldap', help="Filename of LDAP credential config file",
              prompt='LDAP Config Filename', default='connector-ldap.yml')
def example_config(**kwargs):
    """Generate example configuration files"""
    res_files = {
        'root': os.path.join('examples', 'user-sync-config.yml'),
        'umapi': os.path.join('examples', 'connector-umapi.yml'),
        'ldap': os.path.join('examples', 'connector-ldap.yml'),
    }

    for k, fname in kwargs.items():
        assert k in res_files, "Invalid option specified"
        res_file = user_sync.resource.get_resource(res_files[k])
        assert res_file is not None, "Resource file '{}' not found".format(res_files[k])
        click.echo("Generating file '{}'".format(fname))
        shutil.copy(res_file, fname)


@main.command()
@click.help_option('-h', '--help')
def docs():
    """Open user manual in browser"""
    res_file = user_sync.resource.get_resource('manual_url')
    assert res_file is not None, "User Manual URL file not found"
    with click.open_file(res_file) as f:
        url = f.read().strip()
        click.launch(url)


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
    logger.info('Python version: %s.%s.%s on %s' % (sys.version_info[:3] + (sys.platform,)))
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

    post_sync = config_loader.get_post_sync_options()

    config_loader.check_unused_config_keys()

    if directory_connector is not None and directory_connector_options is not None:
        # specify the default user_identity_type if it's not already specified in the options
        if 'user_identity_type' not in directory_connector_options:
            directory_connector_options['user_identity_type'] = rule_config['new_account_type']
        directory_connector.initialize(directory_connector_options)

    additional_group_filters = None
    additional_groups = rule_config.get('additional_groups', None)
    if additional_groups and isinstance(additional_groups, list):
        additional_group_filters = [r['source'] for r in additional_groups]
    if directory_connector is not None:
        directory_connector.state.additional_group_filters = additional_group_filters
        # show error dynamic mappings enabled but 'dynamic_group_member_attribute' is not defined
        if additional_group_filters and directory_connector.state.options['dynamic_group_member_attribute'] is None:
            raise AssertionException(
                "Failed to enable dynamic group mappings. 'dynamic_group_member_attribute' is not defined in config")
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
    rule_processor.run(directory_groups, directory_connector, umapi_connectors, post_sync)

    new_adobe_users = set([u.split(',')[1] for u in
                           list(rule_processor.umapi_info_by_name.values())[0].desired_groups_by_user_key.keys()])
    existing_adobe_users = set([u.split(',')[1] for u in
                                list(rule_processor.umapi_info_by_name.values())[0].umapi_user_by_user_key.keys()])

    if sign_config_file:
        # Need to sleep the application before performing the sync. This is due to the fact that it takes around
        # 30-45 secs for the users to populate into sign.
        logger.info('running Sign sync')
        time.sleep(60)
        sign_sync.run(config_loader, existing_adobe_users | new_adobe_users, sign_config_file)

if __name__ == '__main__':
    main()
