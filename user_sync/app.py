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
import config
import datetime
import logging
import os
import re
import sys

import user_sync.config
import user_sync.error
import user_sync.lockfile
import user_sync.rules
import user_sync.connector.directory
import user_sync.connector.dashboard
from user_sync.version import __version__ as APP_VERSION

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT ='%Y-%m-%d %H:%M:%S'

def process_args():    
    parser = argparse.ArgumentParser(description='Adobe Enterprise Dashboard User Sync')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + APP_VERSION)
    parser.add_argument('-t', '--test-mode',
                        help='run API action calls in test mode (does not execute changes on the Adobe side). Logs '
                             'what would have been executed.',
                        action='store_true', dest='test_mode')
    parser.add_argument('-c', '--config-filename',
                        help='main config filename. (default: "%(default)s")',
                        default=config.DEFAULT_MAIN_CONFIG_FILENAME, metavar='filename', dest='config_filename')
    parser.add_argument('--users',
                        help="specify the users to be considered for sync. Legal values are 'all' (the default), "
                             "'group name or names' (one or more specified AD groups), 'mapped' (all groups listed in "
                             "configuration file), 'file f' (a specified input file).",
                        nargs="*", metavar=('all|file|mapped|group', 'arg1'), dest='users')
    parser.add_argument('--user-filter',
                        help='limit the selected set of users that may be examined for syncing, with the pattern '
                             'being a regular expression.',
                        metavar='pattern', dest='username_filter_pattern')
    parser.add_argument('--source-filter',
                        help='send the file to the specified connector (for example, --source-filter ldap:foo.yml). '
                             'This parameter is used to limit the scope of the LDAP query.',
                        metavar='connector:file', dest='source_filter_args')
    parser.add_argument('--update-user-info',
                        help='if user information differs between the customer side and the Adobe side, the Adobe '
                             'side is updated to match.',
                        action='store_true', dest='update_user_info')
    parser.add_argument('--process-groups',
                        help='if the membership in mapped groups differs between the customer side and the Adobe side, '
                             'the group membership is updated on the Adobe side so that the memberships in mapped '
                             'groups matches the customer side.',
                        action='store_true', dest='manage_groups')
    parser.add_argument('--remove-entitlements-for-strays',
                        help="any 'stray' Adobe users (that is, Adobe users that don't match users on the customer "
                             "side) are removed from all user groups and product configurations on the Adobe side, "
                             "but they are left visible in the Users list in the Adobe console.",
                        action='store_true', dest='disentitle_strays')
    parser.add_argument('--remove-strays',
                        help='like --remove-entitlements-for-strays, but additionally removes stray users '
                             'from the Users list in the Adobe console.  The user account is left intact, with all'
                             'of its associated storage, and can be re-added to the Users list if desired.',
                        action='store_true', dest='remove_strays')
    parser.add_argument('--delete-strays',
                        help='like --remove-strays, but additionally deletes the '
                             '(Enterprise or Federated ID) user account for any '
                             'stray users, so that all of their associated storage is reclaimed and their email '
                             'address is freed up for re-allocation to a new user.',
                        action='store_true', dest='delete_strays')
    parser.add_argument('--output-stray-list',
                        help="any 'stray' Adobe users (that is, Adobe users that don't match users on the customer "
                             "side) are written to a file with the given pathname. "
                             "This file can then be given in the --stray-list argument in a subsequent run.",
                        metavar='output_path', dest='stray_list_output_path')
    parser.add_argument('--input-stray-list',
                        help='causes stray Adobe users to be read from a file with the given pathname rather than'
                             'being computed by matching Adobe users with customer users, '
                             'see --output-stray-list.  When using this option, you must also specify the type'
                             'of stray processing you want done by specifying one of the options '
                             '--remove-entitlements-for-strays, --remove-strays or --delete-strays.',
                        metavar='input_path', dest='stray_list_input_path')
    return parser.parse_args()

def init_console_log():
    console_log_handler = logging.StreamHandler(sys.stdout)
    console_log_handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))
    root_logger = logging.getLogger()
    root_logger.addHandler(console_log_handler)
    root_logger.setLevel(logging.DEBUG)
    return console_log_handler

def init_log(logging_config):
    '''
    :type logging_config: user_sync.config.DictConfig
    '''
    builder = user_sync.config.OptionsBuilder(logging_config)
    builder.set_bool_value('log_to_file', False)
    builder.set_string_value('file_log_directory', 'logs')
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
    if (console_log_level == None):
        console_log_level = logging.INFO
        logger.log(logging.WARNING, 'Unknown console log level: %s setting to info' % options['console_log_level'])
    console_log_handler.setLevel(console_log_level)


    if options['log_to_file'] == True:
        unknown_file_log_level = False
        file_log_level = level_lookup.get(options['file_log_level'])
        if (file_log_level == None):
            file_log_level = logging.INFO
            unknown_file_log_level = True
        file_log_directory = options['file_log_directory']
        if not os.path.exists(file_log_directory):
            os.makedirs(file_log_directory)
        
        file_path = os.path.join(file_log_directory, datetime.date.today().isoformat() + ".log")
        fileHandler = logging.FileHandler(file_path)
        fileHandler.setLevel(file_log_level)
        fileHandler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))        
        logging.getLogger().addHandler(fileHandler)
        if (unknown_file_log_level == True):
            logger.log(logging.WARNING, 'Unknown file log level: %s setting to info' % options['file_log_level'])
        
def begin_work(config_loader):
    '''
    :type config_loader: user_sync.config.ConfigLoader
    '''

    directory_groups = config_loader.get_directory_groups()
    owning_dashboard_config = config_loader.get_dashboard_options_for_owning()
    accessor_dashboard_configs = config_loader.get_dashboard_options_for_accessors()
    rule_config = config_loader.get_rule_options()

    # process mapped configuration after the directory groups have been loaded, as mapped setting depends on this.
    if (rule_config['directory_group_mapped']):
        rule_config['directory_group_filter'] = set(directory_groups.iterkeys())

    referenced_organization_names = set()
    for groups in directory_groups.itervalues():
        for group in groups:
            organization_name = group.organization_name
            if (organization_name != user_sync.rules.OWNING_ORGANIZATION_NAME):
                referenced_organization_names.add(organization_name)
    referenced_organization_names.difference_update(accessor_dashboard_configs.iterkeys())
    
    if (len(referenced_organization_names) > 0):
        raise user_sync.error.AssertionException('dashboard_groups have references to unknown accessor dashboards: %s' % referenced_organization_names) 
                
    directory_connector = None
    directory_connector_options = None
    directory_connector_module_name = config_loader.get_directory_connector_module_name()
    if (directory_connector_module_name != None):
        directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])    
        directory_connector = user_sync.connector.directory.DirectoryConnector(directory_connector_module)        
        directory_connector_options = config_loader.get_directory_connector_options(directory_connector.name)

    config_loader.check_unused_config_keys()
        
    if (directory_connector != None and directory_connector_options != None):
        # specify the default user_identity_type if it's not already specified in the options
        if 'user_identity_type' not in directory_connector_options:
            directory_connector_options['user_identity_type'] = rule_config['new_account_type']
        directory_connector.initialize(directory_connector_options)
    
    dashboard_owning_connector = user_sync.connector.dashboard.DashboardConnector("owning", owning_dashboard_config)
    dashboard_accessor_connectors = {}    
    for accessor_organization_name, accessor_config in accessor_dashboard_configs.iteritems():
        dashboard_accessor_conector = user_sync.connector.dashboard.DashboardConnector("accessor.%s" % accessor_organization_name, accessor_config)
        dashboard_accessor_connectors[accessor_organization_name] = dashboard_accessor_conector 
    dashboard_connectors = user_sync.rules.DashboardConnectors(dashboard_owning_connector, dashboard_accessor_connectors)

    rule_processor = user_sync.rules.RuleProcessor(rule_config)
    if (len(directory_groups) == 0 and rule_processor.will_manage_groups()):
        logger.warn('no groups mapped in config file')
    rule_processor.run(directory_groups, directory_connector, dashboard_connectors)
    
    
def create_config_loader(args):
    config_bootstrap_options = {
        'main_config_filename': args.config_filename,
    }
    config_loader = user_sync.config.ConfigLoader(config_bootstrap_options)
    return config_loader
            
def create_config_loader_options(args):
    config_options = {
        'test_mode': args.test_mode,        
        'manage_groups': args.manage_groups,
        'update_user_info': args.update_user_info,
        'directory_group_mapped': False,
    }

    users_args = args.users
    if users_args is not None:
        users_action = None if len(users_args) == 0 else user_sync.helper.normalize_string(users_args.pop(0))
        if (users_action == None or users_action == 'all'):
            config_options['directory_connector_module_name'] = 'user_sync.connector.directory_ldap'
        elif (users_action == 'file'):
            if (len(users_args) == 0):
                raise user_sync.error.AssertionException('Missing file path for --users %s [file_path]' % users_action)
            config_options['directory_connector_module_name'] = 'user_sync.connector.directory_csv'
            config_options['directory_connector_overridden_options'] = {'file_path': users_args.pop(0)}
        elif (users_action == 'mapped'):
            config_options['directory_connector_module_name'] = 'user_sync.connector.directory_ldap'
            config_options['directory_group_mapped'] = True
        elif (users_action == 'group'):            
            if (len(users_args) == 0):
                raise user_sync.error.AssertionException('Missing groups for --users %s [groups]' % users_action)
            config_options['directory_connector_module_name'] = 'user_sync.connector.directory_ldap'
            config_options['directory_group_filter'] = users_args.pop(0).split(',')
        else:
            raise user_sync.error.AssertionException('Unknown argument --users %s' % users_action)
    
    username_filter_pattern = args.username_filter_pattern 
    if (username_filter_pattern):
        try:
            compiled_expression = re.compile(username_filter_pattern, re.IGNORECASE)
        except Exception as e:
            raise user_sync.error.AssertionException("Bad regular expression for --user-filter: %s reason: %s" % (username_filter_pattern, e.message))
        config_options['username_filter_regex'] = compiled_expression
    
    # --input-stray-list
    stray_list_input_path = args.stray_list_input_path
    if (stray_list_input_path != None):
        if users_args is not None:
            raise user_sync.error.AssertionException('You cannot specify both --users and --input-stray-list')
        # don't read the directory when processing from the stray list
        config_options['directory_connector_module_name'] = None
        logger.info('--input-stray-list specified, so not reading and comparing directory and Adobe users')
        logger.info('Reading stray list from: %s', stray_list_input_path)
        stray_key_list = user_sync.rules.RuleProcessor.read_remove_list(stray_list_input_path, logger = logger)
        logger.info('Total users in stray list: %d', len(stray_key_list))
        config_options['stray_key_list'] = stray_key_list

    # --output-stray-list
    stray_list_output_path = args.stray_list_output_path
    if (stray_list_output_path != None):
        if stray_list_input_path:
            raise user_sync.error.AssertionException('You cannot specify both '
                                                     '--input-stray-list and --output-stray-list')
        logger.info('Writing stray list to: %s', stray_list_output_path)
        config_options['stray_list_output_path'] = stray_list_output_path

    # keep track of the number user removal type commands
    stray_processing_command_count = 0

    # --remove-strays
    remove_strays = args.remove_strays
    if remove_strays:
        if stray_list_output_path:
            remove_strays = False
            logger.warn('--remove-strays ignored when --output-stray-list is specified')
        stray_processing_command_count += 1
    config_options['remove_strays'] = remove_strays

    # --delete-strays
    delete_strays = args.delete_strays
    if delete_strays:
        if stray_list_output_path:
            delete_strays = False
            logger.warn('--delete-strays ignored when --output-stray-list is specified')
        stray_processing_command_count += 1
    config_options['delete_strays'] = delete_strays

    # --remove-entitlements-for-strays
    disentitle_strays = args.disentitle_strays
    if disentitle_strays:
        if stray_list_output_path:
            disentitle_strays = False
            logger.warn('--remove-entitlements-for-strays ignored when --output-stray-list is specified')
        stray_processing_command_count += 1
    config_options['disentitle_strays'] = disentitle_strays

    # ensure the user has only entered one "remove user" type command.    
    if stray_processing_command_count > 1:
        raise user_sync.error.AssertionException('You cannot specify more than one of '
                                                 '--remove-entitlements-for-strays, --remove-strays '
                                                 'and --delete-strays')
                    
    source_filter_args = args.source_filter_args
    if (source_filter_args != None):
        source_filter_args_separator_index = source_filter_args.find(':')
        if (source_filter_args_separator_index >= 0):
            connector_name = source_filter_args[:source_filter_args_separator_index]
            source_filter_file_path = source_filter_args[source_filter_args_separator_index + 1:]
            config_options['directory_source_filters'] = {
                connector_name: source_filter_file_path
            }
        else:
            raise user_sync.error.AssertionException("Invalid arg for --source-filter: %s" % source_filter_args)
    
    return config_options

def log_parameters(args):
    '''
    Log the invocation parameters to make it easier to diagnose problem with customers
    :param args: namespace
    :return: None
    '''
    logger.info('------- Invocation parameters -------')
    logger.info(' '.join(sys.argv))
    logger.info('-------- Internal parameters --------')
    for parameter_name, parameter_value in args.__dict__.iteritems():
        logger.info('  %s: %s', parameter_name, parameter_value)
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
            logger.info("Process is already locked")
        
    except user_sync.error.AssertionException as e:
        if (not e.is_reported()):
            logger.critical(e.message)
            e.set_reported()    
    except:
        try:
            logger.error('Unhandled exception', exc_info=sys.exc_info())
        except:        
            pass
        
    finally:
        if (run_stats != None):
            run_stats.log_end(logger)
        
console_log_handler = init_console_log()
logger = logging.getLogger('main')

if __name__ == '__main__':
    main()
    
