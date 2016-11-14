import argparse
import config
import datetime
import logging
import os
import re
import sys
import lockfile

import rules
import connector.dashboard
import connector.directory

APP_VERSION = "0.6.0"

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT ='%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=LOG_STRING_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.DEBUG)
logger = logging.getLogger('main')

def error_hook(exctype, value, tb):
    """Set up the Error Hook (default exception handler)"""
    try:
        logger.error('Unhandled exception', exc_info=(exctype, value, tb))
    except:
        pass

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
                        nargs="+", default=['all'], metavar=('all|file|group', 'arg1'), dest='users')
    parser.add_argument('--user-filter',
                        help='limit the selected set of users that may be examined for syncing, with the pattern being a regular expression.',
                        metavar='pattern', dest='username_filter_pattern')
    parser.add_argument('--update-user-info', 
                        help="if user information differs between the customer side and the Adobe side, the Adobe side is updated to match.", 
                        action='store_true', dest='update_user_info')
    parser.add_argument('--process-groups', 
                        help="if the membership in mapped groups differs between the customer side and the Adobe side, the group membership is updated on the Adobe side so that the memberships in mapped groups matches the customer side.", 
                        action='store_true', dest='manage_products')
    parser.add_argument('--remove-nonexistent-users',
                        help='Causes the user sync tool to remove Federated users that exist on the Adobe side if they are not in the customer side AD. This has the effect of deleting the user account if that account is owned by the organization under which the sync operation is being run.',
                        action='store_true', dest='remove_nonexistent_users')
    parser.add_argument('--generate-remove-list',
                        help='processing similar to --remove-nonexistent-users except that rather than performing removals, a file is generated (with the given pathname) listing users who would be removed. This file can then be given in the --remove-list argument in a subsequent run.',
                        metavar='output_path', dest='remove_list_output_path')
    parser.add_argument('-d', '--remove-list',
                        help='specifies the file containing the list of users to be removed. Users on this list are removeFromOrg\'d on the Adobe side.',
                        metavar='input_path', dest='remove_list_input_path')
    return parser.parse_args()

def init_log(caller_options):
    '''
    :type caller_options:dict
    '''
    options = {
        'log_to_file': False,
        'file_log_directory': 'logs',
        'file_log_level': 'debug'
    }
    if (caller_options != None):
        options.update(caller_options)
    
    if options['log_to_file'] == True:
        level_lookup = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        file_logging_level = level_lookup.get('file_log_level', logging.NOTSET)
        file_log_directory = options['file_log_directory']
        if not os.path.exists(file_log_directory):
            os.makedirs(file_log_directory)
        
        file_path = os.path.join(file_log_directory, datetime.date.today().isoformat() + ".log")
        fileHandler = logging.FileHandler(file_path)
        fileHandler.setLevel(file_logging_level)
        fileHandler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))        
        logging.getLogger().addHandler(fileHandler)
        
def begin_work(config_loader):
    '''
    :type config_loader: config.ConfigLoader
    '''    
    directory_connector_module_name = config_loader.get_directory_connector_module_name()
    directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])    
    directory_connector = connector.directory.DirectoryConnector(directory_connector_module)
    
    directory_connector_options = config_loader.get_directory_connector_options(directory_connector.name)
    directory_connector.initialize(directory_connector_options)
    
    dashboard_config = config_loader.get_dashboard_config()
    dashboard_owning_connector = connector.dashboard.DashboardConnector(dashboard_config['owning'])
    dashboard_trustee_connectors = {}    
    for trustee_organization_name, trustee_config in dashboard_config['trustees'].iteritems():
        dashboard_trustee_conector = connector.dashboard.DashboardConnector(trustee_config)
        dashboard_trustee_connectors[trustee_organization_name] = dashboard_trustee_conector 
    dashboard_connectors = rules.DashboardConnectors(dashboard_owning_connector, dashboard_trustee_connectors)

    rule_config = config_loader.get_rule_config()
    rule_processor = rules.RuleProcessor(rule_config)
    rule_processor.read_desired_user_products(config_loader.get_directory_groups(), directory_connector)
    rule_processor.process_dashboard_users(dashboard_connectors)
    rule_processor.clean_dashboard_users(dashboard_connectors)
    
    dashboard_connectors.execute_actions()
    
def main():    
    args = process_args()

    config_bootstrap_options = {
        'config_directory': args.config_path,
        'main_config_filename': args.config_filename,
    }        
    config_loader = config.ConfigLoader(config_bootstrap_options)
    init_log(config_loader.get_logging_config())
    
    config_options = {
        'test_mode': args.test_mode,        
        'manage_products': args.manage_products,
        'update_user_info': args.update_user_info
    }

    users_args = args.users
    users_action = users_args.pop(0)
    if (users_action == 'file'):
        if (len(users_args) == 0):
            logger.error('Missing file path for --users %s [file_path]' % users_action)
            return
        config_options['directory_connector_module_name'] = 'connector.directory_csv'
        config_options['directory_connector_overridden_options'] = {'file_path': users_args.pop(0)}
    elif (users_action == 'group'):            
        if (len(users_args) == 0):
            logger.error('Missing groups for --users %s [groups]' % users_action)
            return
        config_options['directory_group_filter'] = users_args.pop(0).split(',')
    
    if (args.username_filter_pattern):
        config_options['username_filter_regex'] = re.compile(args.username_filter_pattern, re.IGNORECASE)
    
    remove_list_input_path = args.remove_list_input_path
    if (remove_list_input_path != None):
        logger.info('Reading remove list from: %s', remove_list_input_path)
        config_options['remove_user_key_list'] = remove_user_key_list = rules.RuleProcessor.read_remove_list(remove_list_input_path)
        logger.info('Total users in remove list: %d', len(remove_user_key_list))
    
    config_options['remove_list_output_path'] = remove_list_output_path = args.remove_list_output_path
    remove_nonexistent_users = args.remove_nonexistent_users
    if (remove_nonexistent_users and remove_list_output_path):
        remove_nonexistent_users = False
        logger.warn('--remove-nonexistent-users ignored when --generate-remove-list is specified')    
    config_options['remove_nonexistent_users'] = remove_nonexistent_users
                    
    config_loader.set_options(config_options)
    
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    lock_path = os.path.join(script_dir, 'lockfile')
    lock = lockfile.ProcessLock(lock_path)
    if lock.set_lock():
        try:
            begin_work(config_loader)
        finally:
            lock.unlock()
    else:
        logger.info("Process is already locked")


if __name__ == '__main__':
    #set up exception hook
    sys.excepthook = error_hook
    
    main()
    
    
