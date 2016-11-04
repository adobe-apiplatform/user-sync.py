import argparse
import config
import datetime
import logging
import os
import sys
import lockfile

APP_VERSION = "0.6.0"

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT ='%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=LOG_STRING_FORMAT, datefmt=LOG_DATE_FORMAT, level=logging.DEBUG)

def error_hook(exctype, value, tb):
    """Set up the Error Hook (default exception handler)"""
    try:
        logging.getLogger('main').error('Exception %s: %s', exctype, value)
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
                        help='specify path to config files. Default is the current directory.',
                        action='store_true', default=config.DEFAULT_CONFIG_DIRECTORY, dest='config_path')
    parser.add_argument('--config-filename',
                        default=config.DEFAULT_MAIN_CONFIG_FILENAME, dest='config_filename')
    parser.add_argument('--users', 
                        help="specify the users to be considered for sync. Legal values are 'all' (the default), 'group name or names' (one or more specified AD groups), 'file f' (a specified input file).", 
                        action='append', nargs="+", default=['all'], metavar=('all|file|group', 'arg1'), dest='users')
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

def main():    
    args = process_args()
    
    config_options = {
        'directory': args.config_path,
        'main_config_filename': args.config_filename
    }
    config_loader = config.ConfigLoader(config_options)
    main_config = config_loader.load_main_config()    
    init_log(main_config.get('logging'))
    
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    lock_path = os.path.join(script_dir, 'lockfile')
    lock = lockfile.ProcessLock(lock_path)
    if lock.set_lock():
        try:
            pass
        finally:
            lock.unlock()
    else:
        logging.getLogger('main').info("Process is already locked")


if __name__ == '__main__':
    #set up exception hook
    sys.excepthook = error_hook
    
    main()
    
