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
import logging
import os
import platform
import sys
import json
from datetime import datetime
from pathlib import Path

import click
from click_default_group import DefaultGroup
from urllib3.exceptions import InsecureRequestWarning
import requests

import user_sync.certgen
import user_sync.cli
from user_sync.config.error import ConfigValidationError
import user_sync.config.sign_sync
import user_sync.config.user_sync
import user_sync.connector.connector_umapi
import user_sync.connector.directory
import user_sync.encryption
import user_sync.engine.umapi
import user_sync.helper
import user_sync.lockfile
from user_sync import resource
from user_sync.config.user_sync import UMAPIConfigLoader
from user_sync.config.sign_sync import SignConfigLoader
from user_sync.config import user_sync as config
from user_sync.config.common import ConfigLoader, OptionsBuilder
from user_sync.connector.connector_umapi import UmapiConnector
from user_sync.engine.common import PRIMARY_TARGET_NAME
from user_sync.engine.sign import SignSyncEngine
from user_sync.connector.directory import DirectoryConnector
from user_sync.connector.directory_adobe_console import AdobeConsoleConnector
from user_sync.connector.directory_csv import CSVDirectoryConnector
from user_sync.connector.directory_ldap import LDAPDirectoryConnector
from user_sync.connector.directory_okta import OktaDirectoryConnector

from user_sync.error import AssertionException
from user_sync.version import __version__ as app_version

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

EXIT_CODE = 0

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
def info():
    """Get a dump of environmental information"""
    click.echo(f"Python: {platform.python_version()}")
    plat = platform.platform()
    click.echo(f"Platform: {plat}")
    if 'linux' in plat.lower():
        click.echo("OS Release Info:")
        with open('/etc/os-release') as f:
            for l in f:
                click.echo(f"  {l.strip()}")
    click.echo("Packages:")
    pkg_meta_file = resource.get_resource('pkg_meta.json')
    with open(pkg_meta_file) as f:
        pkg_meta = json.load(f) 
        for p in sorted(pkg_meta):
            click.echo(f"  {p}: {pkg_meta[p]}")


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
    # sign_config_file = kwargs.get('sign_sync_config')
    # if 'sign_sync_config' in kwargs:
    #     del (kwargs['sign_sync_config'])
    try:
        run_sync(config.UMAPIConfigLoader(kwargs), begin_work_umapi)
    except AssertionException as e:
        if not e.is_reported():
            logger.critical("%s", e)
            e.set_reported()


@main.command()
@click.help_option('-h', '--help')
@click.option('-c', '--config-filename',
              help="path to your main configuration file",
              type=str,
              nargs=1,
              metavar='path-to-file')  # default should be sign-sync-config.yml
@click.option('--users',
              help="specify the users to be considered for sync. Legal values are 'all' (the default), "
                   "'group names' (a comma-separated list of groups in the enterprise "
                   "directory, and only users in those groups are selected), 'mapped' (all groups listed in "
                   "the configuration file).",
              cls=user_sync.cli.OptionMulti,
              type=list,
              metavar='all|mapped|group [group list]')  # default should mapped
@click.option('-t/-T', '--test-mode/--no-test-mode', default=None,
              help='enable test mode (API calls do not execute changes).')
def sign_sync(**kwargs):
    """Run Sign Sync """
    # load the config files (sign-sync-config.yml) and start the file logger
    try:
        run_sync(SignConfigLoader(kwargs), begin_work_sign)
    except ConfigValidationError as e:
        logger.critical('Schema validation failed. Detailed message: {}'.format(e))
    except AssertionException as e:
        if not e.is_reported():
            logger.critical("%s", e)
            e.set_reported()


@main.command()
@click.help_option('-h', '--help')
@click.option('--config-filename', help="Filename of post-sync config file",
              prompt='Post-Sync Config File', default='connector-sign-sync.yml')
@click.option('--connector-type', help="Type of identity connector",
              prompt='Connector Type', default='ldap')
@click.option('--connector-filename', help="Filename of connector file",
              prompt='Connector Filename', default='connector-ldap.yml')
def migrate_post_sync(config_filename, connector_type, connector_filename):
    """Migrate post-sync config (connector-sign-sync.yml) to new Sign Sync config files"""
    import yaml

    click.echo(f"Using '{config_filename}'")
    config_path = Path(config_filename)
    if not config_path.is_file() or not config_path.exists():
        raise AssertionException(f"Post-sync config file '{config_path}' not found")
    post_sync_config: dict = yaml.safe_load(config_path.open())

    sign_sync_data = {
        'sign_orgs': [],
        'identity_source': {
            'type': connector_type,
            'connector': connector_filename,
        },
        'user_sync': {
            'sign_only_limit': 100,
            'sign_only_user_action': 'reset',
        },
        'cache': {
            'path': 'cache/sign',
        },
        'logging': {
            'log_to_file': True,
            'file_log_directory': 'sign_logs',
            'file_log_name_format': '{:%Y-%m-%d}-sign.log',
            'file_log_level': 'info',
            'console_log_level': 'debug',
        },
        'invocation_defaults': {
            'users': 'mapped',
            'test_mode': False,
        },
        'user_management': [],
    }

    # first, generate connector config files
    # derive base path for new files based on post-sync config path
    base_path = config_path.parent

    sign_orgs: list[dict] = post_sync_config.get('sign_orgs', [])
    for sign_org in sign_orgs:
        console_org = sign_org.get('console_org')
        if console_org is None:
            connector_filename = base_path / 'connector-sign.yml'
            target_id = 'primary'
        else:
            connector_filename = base_path / f'connector-sign-{console_org}.yml'
            target_id = console_org
        connector_data = {
            'host': sign_org.get('host'),
            'integration_key': sign_org.get('key'),
            'admin_email': sign_org.get('admin_email'),
            # since post-sync is always GPS, we can default these to False
            'create_users': False,
            'deactivate_users': False,
        }
        with connector_filename.open('w') as fp:
            yaml.dump(connector_data, fp)
        click.echo(f"Created connector file '{connector_filename}'")
        sign_sync_data['sign_orgs'].append({target_id: str(connector_filename.name)})

    # second, create group mapping definitions
    # define pure group mappings first
    user_groups: list[str] = post_sync_config.get('user_groups', [])
    for user_group in user_groups:
        group_parts = user_group.split('::')
        if len(group_parts) > 1:
            source_group = group_parts[1]
        else:
            source_group = user_group
        mapping = {
            'directory_group': source_group,
            'sign_group': user_group,
            'group_admin': False,
            'account_admin': False,
        }
        sign_sync_data['user_management'].append(mapping)

    # now define admin role mappings
    admin_roles: list[dict] = post_sync_config.get('admin_roles', [])
    for admin_role in admin_roles:
        is_acct_admin = admin_role['sign_role'] == 'ACCOUNT_ADMIN'
        is_group_admin = admin_role['sign_role'] == 'GROUP_ADMIN'
        adobe_groups: list[str] = admin_role.get('adobe_groups', [])
        for adobe_group in adobe_groups:
            mapping = {
                'directory_group': adobe_group,
                'sign_group': None,
                'group_admin': is_group_admin,
                'account_admin': is_acct_admin,
            }
            sign_sync_data['user_management'].append(mapping)

    sign_sync_filename = base_path / 'sign-sync-config.yml'
    yaml.dump(sign_sync_data, sign_sync_filename.open('w'))
    click.echo(f"Created Sign Sync config file '{sign_sync_filename}'")
    click.echo(f"Migration complete. You can now safely delete '{config_path}'")
    click.echo("Your 'post_sync' config should be removed from user-sync-config.yml")
    click.echo("\nIMPORTANT - please review 'sign-sync-config.yml' for accuracy. Some settings,")
    click.echo("  such as group mapping, may need to be manually adjusted.")
    click.echo("\nYou can test your Sign sync by running `./user-sync sign-sync -t`")


def begin_work_sign(sign_config_loader: SignConfigLoader):
    sign_engine_config = sign_config_loader.get_engine_options()
    directory_connector, directory_groups = load_directory_config(sign_config_loader)
    target_options = sign_config_loader.get_target_options()
    sign_engine = SignSyncEngine(sign_engine_config, target_options)
    sign_engine.run(directory_groups, directory_connector)


def begin_work_umapi(config_loader: UMAPIConfigLoader):
    """
    :type config_loader: config.UMAPIConfigLoader
    """

    umapi_engine_config = config_loader.get_engine_options()
    directory_connector, directory_groups = load_directory_config(config_loader, umapi_engine_config['new_account_type'])

    if not umapi_engine_config['ssl_cert_verify']:
        logger.warning("SSL certificate verification is bypassed.  Consider disabling this option and using the "
                       "REQUESTS_CA_BUNDLE environment variable to specify the PEM firewall bundle...")
        # Suppress only the single warning from urllib3 needed.
        # noinspection PyUnresolvedReferences
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # make sure that all the adobe groups are from known umapi connector names
    primary_umapi_config, secondary_umapi_configs = config_loader.get_target_options()
    referenced_umapi_names = set()
    for groups in directory_groups.values():
        for group in groups:
            umapi_name = group.umapi_name
            if umapi_name != PRIMARY_TARGET_NAME:
                referenced_umapi_names.add(umapi_name)
    referenced_umapi_names.difference_update(secondary_umapi_configs.keys())
    if len(referenced_umapi_names) > 0:
        raise AssertionException('Adobe groups reference unknown umapi connectors: %s' % referenced_umapi_names)

    config_loader.check_unused_config_keys()

    additional_group_filters = None
    additional_groups = umapi_engine_config.get('additional_groups', None)
    if additional_groups and isinstance(additional_groups, list):
        additional_group_filters = [r['source'] for r in additional_groups]
    if directory_connector is not None:
        directory_connector.set_additional_group_filters(additional_group_filters)

    primary_name = '.primary' if secondary_umapi_configs else ''
    umapi_primary_connector = UmapiConnector(primary_name, primary_umapi_config, True)
    umapi_other_connectors = {}
    for secondary_umapi_name, secondary_config in secondary_umapi_configs.items():
        umapi_secondary_conector = UmapiConnector(".secondary.%s" % secondary_umapi_name,
                                                  secondary_config)
        umapi_other_connectors[secondary_umapi_name] = umapi_secondary_conector
    umapi_connectors = user_sync.engine.umapi.UmapiConnectors(umapi_primary_connector, umapi_other_connectors)

    rule_processor = user_sync.engine.umapi.RuleProcessor(umapi_engine_config)
    if len(directory_groups) == 0 and rule_processor.will_process_groups():
        logger.warning('No group mapping specified in configuration but --process-groups requested on command line')
    rule_processor.run(directory_groups, directory_connector, umapi_connectors)


def load_directory_config(config_loader: ConfigLoader, new_account_type=None) -> tuple[DirectoryConnector, dict]:

    # Group mappings from the sign or umapi sync config files
    directory_groups = config_loader.get_directory_groups()

    directory_connector = None
    directory_connector_options = None
    directory_connector_module_name = config_loader.get_directory_connector_module_name()
    if directory_connector_module_name is not None:
        if directory_connector_module_name == 'ldap':
            directory_connector = LDAPDirectoryConnector
        elif directory_connector_module_name == 'okta':
            directory_connector = OktaDirectoryConnector
        elif directory_connector_module_name == 'csv':
            directory_connector = CSVDirectoryConnector
        elif directory_connector_module_name == 'adobe_console':
            directory_connector = AdobeConsoleConnector
        else:
            raise AssertionException('Directory connector not found.')

        directory_connector_options = config_loader.get_directory_connector_options(directory_connector.name)

    if directory_connector is not None and directory_connector_options is not None:
        # specify the default user_identity_type if it's not already specified in the options
        # this has no effect for sign sync, but directory connector
        if new_account_type and 'user_identity_type' not in directory_connector_options:
            directory_connector_options['user_identity_type'] = new_account_type
        directory_connector = directory_connector(directory_connector_options)

    return directory_connector, directory_groups


def run_sync(config_loader, begin_work):
    run_stats = None
    global EXIT_CODE
    try:
        init_log(config_loader.get_logging_config())

        test_mode = " (TEST MODE)" if config_loader.get_invocation_options()['test_mode'] else ''
        # add start divider, app version number, and invocation parameters to log
        run_stats = user_sync.helper.JobStats('Run (User Sync version: ' + app_version + ')' + test_mode, divider='=')
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
            EXIT_CODE = 1
            e.set_reported()
    except KeyboardInterrupt:
        try:
            logger.critical('Keyboard interrupt, exiting immediately.')
        except Exception:
            pass
    except Exception:
        try:
            logger.critical('Unhandled exception', exc_info=sys.exc_info())
            EXIT_CODE = 1
        except Exception:
            pass

    finally:
        if run_stats is not None:
            run_stats.log_end(logger)
    sys.exit(EXIT_CODE)


# Additional CLI commands #

@main.command(short_help="Generate conf files, certificates and shell scripts")
@click.help_option('-h', '--help')
@click.pass_context
def init(ctx):
    """
    Generates configuration files, an X509 certificate/keypair, and the batch files for running the user-sync tool
    in test and live mode.
    """
    ctx.forward(shell_scripts, platform=None)

    sync = 'user-sync-config.yml'
    umapi = 'connector-umapi.yml'
    ldap = 'connector-ldap.yml'
    ctx.forward(example_config, root=sync, umapi=umapi, ldap=ldap)


@main.command(short_help="Generate invocation scripts")
@click.help_option('-h', '--help')
@click.option('-p', '--platform', help="Platform for which to generate scripts [default: current system platform]",
              type=click.Choice(['win', 'linux'], case_sensitive=False))
def shell_scripts(platform):
    """Generate invocation shell scripts for the given platform."""
    if platform is None:
        platform = 'win' if 'win' in sys.platform.lower() else 'linux'
    shell_scripts = resource.get_resource_dir('shell_scripts/{}'.format(platform))
    for script in shell_scripts:
        with open(script, 'r') as fh:
            content = fh.read()
        target = Path.cwd() / Path(script).parts[-1]
        if target.exists() and not click.confirm('\nWarning - file already exists: \n{}\nOverwrite?'.format(target)):
            continue
        with open(str(target), 'w') as fh:
            fh.write(content)
        click.echo("Wrote shell script: {}".format(target))


@main.command()
@click.help_option('-h', '--help')
def docs():
    """Open user manual in browser"""
    res_file = resource.get_resource('manual_url')
    assert res_file is not None, "User Manual URL file not found"
    with click.open_file(res_file) as f:
        url = f.read().strip()
        click.launch(url)


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
        target = Path.cwd() / fname
        assert k in res_files, "Invalid option specified"
        res_file = resource.get_resource(res_files[k])
        assert res_file is not None, "Resource file '{}' not found".format(res_files[k])
        if target.exists() and not click.confirm('\nWarning - file already exists: \n{}\nOverwrite?'.format(target)):
            continue
        click.echo("Generating file '{}'".format(fname))
        with open(res_file, 'r') as file:
            content = file.read()
        with open(target, 'w') as file:
            file.write(content)


@main.command()
@click.help_option('-h', '--help')
@click.option('--root', help="Filename of root sign sync config file",
              prompt='Main Config Filename', default='sign-sync-config.yml')
@click.option('--sign', help="Filename of Sign Sync config",
              prompt='Sign Sync Config Filename', default='connector-sign.yml')
@click.option('--ldap', help="Filename of LDAP credential config file",
              prompt='LDAP Config Filename', default='connector-ldap.yml')
def example_config_sign(**kwargs):
    """Generate Sign Sync Config"""
    res_files = {
        'root': os.path.join('examples', 'sign-sync-config.yml'),
        'sign': os.path.join('examples', 'connector-sign.yml'),
        'ldap': os.path.join('examples', 'connector-ldap.yml'),
    }

    for k, fname in kwargs.items():
        target = Path.cwd() / fname
        assert k in res_files, "Invalid option specified"
        res_file = resource.get_resource(res_files[k])
        assert res_file is not None, "Resource file '{}' not found".format(res_files[k])
        if target.exists() and not click.confirm('\nWarning - file already exists: \n{}\nOverwrite?'.format(target)):
            continue
        click.echo("Generating file '{}'".format(fname))
        with open(res_file, 'r') as file:
            content = file.read()
        with open(target, 'w') as file:
            file.write(content)


def init_log(logging_config):
    """
    :type logging_config: user_sync.config.DictConfig
    """

    def progress(self, count, total, message="", *args, **kws):
        if self.show_progress:
            count = int(count)
            total = int(total)
            percent_done = round(100*count/total, 1) if total > 0 else 0
            message = "{0}/{1} ({2}%) {3}".format(count, total, percent_done, message)
        if message:
            self._log(logging.INFO, message, args, **kws)
    logging.Logger.progress = progress

    builder = OptionsBuilder(logging_config)
    builder.set_bool_value('log_to_file', False)
    builder.set_string_value('file_log_directory', 'logs')
    builder.set_string_value('file_log_name_format', '{:%Y-%m-%d}.log')
    builder.set_string_value('file_log_level', 'info')
    builder.set_string_value('console_log_level', 'info')
    builder.set_bool_value('log_progress', True)
    options = builder.get_options()

    level_lookup = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    logging.Logger.show_progress = bool(options['log_progress'])
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
    logger.info('User Sync {0} - Python {1} - {2} {3}'
                .format(app_version, platform.python_version(), platform.system(), platform.version()))
    logger.info('------- Command line arguments -------')
    logger.info(' '.join(argv))
    logger.debug('-------- Resulting invocation options --------')
    for parameter_name, parameter_value in config_loader.get_invocation_options().items():
        logger.debug('  %s: %s', parameter_name, parameter_value)
    logger.info('-------------------------------------')


@main.command(short_help="Encrypt RSA private key")
@click.help_option('-h', '--help')
@click.argument('key-path', default='private.key', type=click.Path(exists=True))
@click.option('-o', '--output-file', help="Path of encrypted file [default: key specified by KEY_PATH will be overwritten]",
              default=None)
@click.option('--password', '-p', prompt='Create password', hide_input=True, confirmation_prompt=True)
def encrypt(output_file, password, key_path):
    """Encrypt RSA private key specified by KEY_PATH.

       KEY_PATH default: private.key

       A passphrase is required to encrypt the file"""
    if output_file is None:
        output_file = key_path
    if output_file != key_path and Path(output_file).exists() \
            and not click.confirm('\nWarning - file already exists: \n{}\nOverwrite?'.format(output_file)):
        return
    try:
        data = user_sync.encryption.encrypt_file(password, key_path)
        user_sync.encryption.write_key(data, output_file)
        click.echo('Encryption was successful.')
        click.echo('Wrote file: {}'.format(os.path.abspath(output_file)))
    except AssertionException as e:
        click.echo(str(e))


@main.command(short_help="Decrypt RSA private key")
@click.help_option('-h', '--help')
@click.argument('key-path', default='private.key', type=click.Path(exists=True))
@click.option('-o', '--output-file',
              help="Path of decrypted file [default: key specified by KEY_PATH will be overwritten]",
              default=None)
@click.option('--password', '-p', prompt='Enter password', hide_input=True)
def decrypt(output_file, password, key_path):
    """Decrypt RSA private key specified by KEY_PATH.

       KEY_PATH default: private.key

       A passphrase is required to decrypt the file"""
    if output_file is None:
        output_file = key_path
    if output_file != key_path and Path(output_file).exists() \
            and not click.confirm('\nWarning - file already exists: \n{}\nOverwrite?'.format(output_file)):
        return
    try:
        data = user_sync.encryption.decrypt_file(password, key_path)
        user_sync.encryption.write_key(data, output_file)
        click.echo('Decryption was successful.')
        click.echo('Wrote file: {}'.format(os.path.abspath(output_file)))
    except AssertionException as e:
        click.echo(str(e))


@main.command(short_help="Generate service integration certificates")
@click.help_option('-h', '--help')
@click.option('--overwrite', '-o', '-y', help='Overwrite existing files without being asked to confirm', is_flag=True)
@click.option('--randomize', '-r', help='Randomize the values rather than entering credentials', is_flag=True)
@click.option('--key', '-k', help='Set a custom output path for private key', default='private.key')
@click.option('--certificate', '-c', help='Set a custom output path for certificate', default='certificate_pub.crt')
def certgen(randomize, key, certificate, overwrite):
    """
    Generates an X509 certificate/keypair with random or user-specified subject.
    User Sync Tool can use these files to communicate with the admin console.
    Please visit https://console.adobe.io to complete the integration process.
    Use the --randomize argument to create a secure keypair with no user input.
    """
    key = os.path.abspath(key)
    certificate = os.path.abspath(certificate)
    existing = "\n".join({f for f in (key, certificate) if os.path.exists(f)})
    if existing and not overwrite:
        if not click.confirm('\nWarning: files already exist: \n{}\nOverwrite?'.format(existing)):
            return
    try:
        if randomize:
            click.echo("\nSkipping user input due to --randomize flag")
        else:
            click.echo(
                "\nEnter information as required to generate the X509 certificate/key pair for your organization. "
                "This information is used only for authentication with UMAPI and does not need to reflect "
                "an SSL or other official identity.  Specify values as you deem fit.\n")
        subject_fields = user_sync.certgen.get_subject_fields(randomize)
        user_sync.certgen.generate(key, certificate, subject_fields)
        click.echo("----------------------------------------------------")
        click.echo("Success! Files were created at:\n{0}\n{1}".format(key, certificate))
    except AssertionException as e:
        click.echo("Error creating keypair: " + str(e))
        click.echo('Files have not been created/overwritten.')


if __name__ == '__main__':
    main()
