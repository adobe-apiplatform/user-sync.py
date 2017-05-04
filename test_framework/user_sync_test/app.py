import sys
import argparse
import logging
import error
import vcr

from test import UserSyncTestSet
from version import __version__ as APP_VERSION

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_CONFIG_FILENAME = 'test-set-config.yml'

def process_args():
    '''
    Validates the application arguments, and resolves the arguments into a Namespace object.
    :rtype: Namespace object with argument values mapped to destination properties. The mapping is defined in the
        argument parser.
    '''
    parser = argparse.ArgumentParser(description="User Sync Test from Adobe")
    parser.add_argument("-v", "--version",
                        action="version",
                        version="%(prog)s " + APP_VERSION)
    parser.add_argument("-c", "--config-filename",
                        help="main test set config filename.",
                        metavar="filename",
                        dest="config_filename",
                        default=DEFAULT_CONFIG_FILENAME)
    parser.add_argument("-t", "--test-name",
                        help="test name",
                        metavar="name of test",
                        dest="test_name",
                        default=None)
    parser.add_argument("-r", "--record",
                        help="sets the user-sync-test tool in record mode",
                        action="store_true",
                        dest="record_mode",
                        default=False)
    return parser.parse_args()

def init_console_log():
    '''
    Setup the formatting and reporting level of the application log.
    :rtype: StreamHandler
    '''
    console_log_handler = logging.StreamHandler(sys.stdout)
    console_log_handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))
    root_logger = logging.getLogger()
    root_logger.addHandler(console_log_handler)
    root_logger.setLevel(logging.DEBUG)
    logging.getLogger('vcr').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    return console_log_handler

def log_test_set_summary(test_set):
    '''
    Outputs the summary for the test set.
    :param test_set: UserSyncTestSet
    '''
    COUNTER_MAP = [
        ('tests succeeded', test_set.success_count),
        ('tests failed', test_set.fail_count)
    ]

    max_name_len = 0
    for (k, v) in COUNTER_MAP:
        if len(k) > max_name_len:
            max_name_len = len(k)

    logger.info('------------------- Test Summary -------------------')
    for (k, v) in COUNTER_MAP:
        logger.info('%s: %d' % (k.rjust(max_name_len), v))
    logger.info('----------------------------------------------------')


def main():
    try:
        try:
            args = process_args()
        except SystemExit:
            return

        config = {
            'config_filename': args.config_filename,
            'record_mode': args.record_mode,
            'test_name': args.test_name
        }

        test_set = UserSyncTestSet(args.config_filename, config)
        test_set.run()

        log_test_set_summary(test_set)

    except error.AssertionException as e:
        if not e.is_reported():
            logger.critical(e.message)
            e.set_reported()
    except:
        try:
            logger.error('Unhandled exception', exc_info=sys.exc_info())
        except:
            pass
        
logger = logging.getLogger("main")

if __name__ == "__main__":
    init_console_log()
    main()
