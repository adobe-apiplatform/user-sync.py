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

APP_VERSION = "1.0rc1"

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT ='%Y-%m-%d %H:%M:%S'

def process_args():    
    parser = argparse.ArgumentParser(description='Adobe Enterprise Dashboard User Sync')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s ' + APP_VERSION)
    parser.add_argument('-t', '--test-mode',
                        help='run API action calls in test mode (does not execute changes). Logs what would have been executed.',
                        action='store_true', dest='test_mode')
    parser.add_argument('-c', '--config-path',
                        help='specify path to config files. (default: "%(default)s")',
                        default=config.DEFAULT_CONFIG_DIRECTORY, metavar='path', dest='config_path')
    parser.add_argument('--config-filename',
                        help='main config filename. (default: "%(default)s")',
                        default=config.DEFAULT_MAIN_CONFIG_FILENAME, metavar='filename', dest='config_filename')
    parser.add_argument('--users', 
                        help="specify the users to be considered for sync. Legal values are 'all' (the default), 'group name or names' (one or more specified AD groups), 'file f' (a specified input file).", 
                        nargs="*", metavar=('all|file|group', 'arg1'), dest='users')
    parser.add_argument('--user-filter',
                        help='limit the selected set of users that may be examined for syncing, with the pattern being a regular expression.',
                        metavar='pattern', dest='username_filter_pattern')
    parser.add_argument('--source-filter',
                        help='send the file to the specified connector (for example, --source-filter ldap:foo.yml). This parameter is used to limit the scope of the LDAP query.',
                        metavar='connector:file', dest='source_filter_args')
    parser.add_argument('--update-user-info', 
                        help="if user information differs between the customer side and the Adobe side, the Adobe side is updated to match.", 
                        action='store_true', dest='update_user_info')
    parser.add_argument('--process-groups', 
                        help="if the membership in mapped groups differs between the customer side and the Adobe side, the group membership is updated on the Adobe side so that the memberships in mapped groups matches the customer side.", 
                        action='store_true', dest='manage_groups')
    parser.add_argument('--remove-nonexistent-users',
                        help='Causes the user sync tool to remove Federated users that exist on the Adobe side if they are not in the customer side AD. This has the effect of deleting the user account if that account is owned by the organization under which the sync operation is being run.',
                        action='store_true', dest='remove_nonexistent_users')
    parser.add_argument('--generate-remove-list',
                        help='processing similar to --remove-nonexistent-users except that rather than performing removals, a file is generated (with the given pathname) listing users who would be removed. This file can then be given in the --remove-list argument in a subsequent run.',
                        metavar='output_path', dest='remove_list_output_path')
    parser.add_argument('-d', '--remove-list',
                        help='specifies the file containing the list of users to be removed. Users on this list are removeFromOrg\'ed on the Adobe side.',
                        metavar='input_path', dest='remove_list_input_path')
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
    builder.set_string_value('file_log_level', 'debug')
    builder.set_string_value('console_log_level', None)    
    options = builder.get_options()
        
    level_lookup = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    console_log_level = level_lookup.get(options['console_log_level'])
    if (console_log_level != None):
        console_log_handler.setLevel(console_log_level)
    
    if options['log_to_file'] == True:
        file_log_level = level_lookup.get(options['file_log_level'], logging.NOTSET)
        file_log_directory = options['file_log_directory']
        if not os.path.exists(file_log_directory):
            os.makedirs(file_log_directory)
        
        file_path = os.path.join(file_log_directory, datetime.date.today().isoformat() + ".log")
        fileHandler = logging.FileHandler(file_path)
        fileHandler.setLevel(file_log_level)
        fileHandler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))        
        logging.getLogger().addHandler(fileHandler)
        
def begin_work(config_loader):
    '''
    :type config_loader: user_sync.config.ConfigLoader
    '''

    directory_groups = config_loader.get_directory_groups()
    owning_dashboard_config = config_loader.get_dashboard_options_for_owning()
    trustee_dashboard_configs = config_loader.get_dashboard_options_for_trustees()
    rule_config = config_loader.get_rule_options()

    referenced_organization_names = set()
    for groups in directory_groups.itervalues():
        for group in groups:
            organization_name = group.organization_name
            if (organization_name != user_sync.rules.OWNING_ORGANIZATION_NAME):
                referenced_organization_names.add(organization_name)
    referenced_organization_names.difference_update(trustee_dashboard_configs.iterkeys())
    
    if (len(referenced_organization_names) > 0):
        raise user_sync.error.AssertionException('dashboard_groups have references to unknown trustee dashboards: %s' % referenced_organization_names) 
                
    directory_connector = None
    directory_connector_options = None
    directory_connector_module_name = config_loader.get_directory_connector_module_name()
    if (directory_connector_module_name != None):
        directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])    
        directory_connector = user_sync.connector.directory.DirectoryConnector(directory_connector_module)        
        directory_connector_options = config_loader.get_directory_connector_options(directory_connector.name)

    config_loader.check_unused_config_keys()
        
    if (directory_connector != None and directory_connector_options != None):
        directory_connector.initialize(directory_connector_options)
    
    dashboard_owning_connector = user_sync.connector.dashboard.DashboardConnector("owning", owning_dashboard_config)
    dashboard_trustee_connectors = {}    
    for trustee_organization_name, trustee_config in trustee_dashboard_configs.iteritems():
        dashboard_trustee_conector = user_sync.connector.dashboard.DashboardConnector("trustee.%s" % trustee_organization_name, trustee_config)
        dashboard_trustee_connectors[trustee_organization_name] = dashboard_trustee_conector 
    dashboard_connectors = user_sync.rules.DashboardConnectors(dashboard_owning_connector, dashboard_trustee_connectors)

    rule_processor = user_sync.rules.RuleProcessor(rule_config)
    if (len(directory_groups) == 0 and rule_processor.will_manage_groups()):
        logger.warn('no groups mapped in config file')
    rule_processor.run(directory_groups, directory_connector, dashboard_connectors)
    
    
def create_config_loader(args):
    config_bootstrap_options = {
        'config_directory': args.config_path,
        'main_config_filename': args.config_filename,
    }
    config_loader = user_sync.config.ConfigLoader(config_bootstrap_options)
    return config_loader
            
def create_config_loader_options(args):
    config_options = {
        'test_mode': args.test_mode,        
        'manage_groups': args.manage_groups,
        'update_user_info': args.update_user_info,        
    }

    users_args = args.users
    if (users_args != None):
        users_action = None if len(users_args) == 0 else user_sync.helper.normalize_string(users_args.pop(0))
        if (users_action == None or users_action == 'all'):
            config_options['directory_connector_module_name'] = 'user_sync.connector.directory_ldap'
        elif (users_action == 'file'):
            if (len(users_args) == 0):
                raise user_sync.error.AssertionException('Missing file path for --users %s [file_path]' % users_action)
            config_options['directory_connector_module_name'] = 'user_sync.connector.directory_csv'
            config_options['directory_connector_overridden_options'] = {'file_path': users_args.pop(0)}
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
    
    remove_list_input_path = args.remove_list_input_path
    if (remove_list_input_path != None):
        logger.info('Reading remove list from: %s', remove_list_input_path)
        remove_user_key_list = user_sync.rules.RuleProcessor.read_remove_list(remove_list_input_path, logger = logger)
        logger.info('Total users in remove list: %d', len(remove_user_key_list))
        config_options['remove_user_key_list'] = remove_user_key_list
         
    config_options['remove_list_output_path'] = remove_list_output_path = args.remove_list_output_path
    remove_nonexistent_users = args.remove_nonexistent_users
    if (remove_nonexistent_users and remove_list_output_path):
        remove_nonexistent_users = False
        logger.warn('--remove-nonexistent-users ignored when --generate-remove-list is specified')    
    config_options['remove_nonexistent_users'] = remove_nonexistent_users
                    
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

def main():   
    run_stats = None 
    try:
        try:
            args = process_args()
        except SystemExit:
            return
        
        config_loader = create_config_loader(args)
        init_log(config_loader.get_logging_config())
        
        run_stats = user_sync.helper.JobStats("Run", divider = "=")
        run_stats.log_start(logger)

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
            logger.error(e.message)
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
    
