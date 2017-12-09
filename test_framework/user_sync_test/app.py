import sys
import argparse
import logging
import error

import helper
from test import TestSuite
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
    parser.add_argument("-c", "--test-suite-config-filename",
                        help="main test suite config filename.",
                        metavar="filename",
                        dest="config_filename",
                        default=DEFAULT_CONFIG_FILENAME)
    parser.add_argument("-g", "--test-group-name",
                        help="test group to limit testing to.",
                        metavar="group",
                        dest="test_group_name",
                        default=None)
    parser.add_argument("-t", "--test",
                        help="test name",
                        metavar="name of test",
                        dest="test_name",
                        default=None)
    parser.add_argument("-l", "--live",
                        help="sets the user-sync-test tool in Live mode, which directs user-sync to communicate "
                             "with the ummapi server, and overwrites any recorded session with the communication "
                             "and output from this new live session. (Playback mode is the default mode.)",
                        action="store_true",
                        dest="live_mode")
    parser.add_argument("-p", "--playback",
                        help="sets the user-sync-test tool in Playback mode, which suppresses any communication "
                             "with the umapi server, and instead plays back the responses recorded from the server "
                             "during the last live session. (This is the default mode.)",
                        action="store_false",
                        dest="live_mode")
    parser.set_defaults(live_mode=False)
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
    root_logger.setLevel(logging.INFO)
    logging.getLogger('vcr').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('BaseHTTPServer').setLevel(logging.WARNING)
    logging.getLogger('test-server').setLevel(logging.INFO)
    return console_log_handler

def log_test_set_summary(live_mode):
    '''
    Outputs the summary for the test set.
    :param test_set: UserSyncTestSet
    '''
    if live_mode:
        COUNTER_MAP = [
            ('tests recorded', helper.JobStats.test_success_count),
            ('tests not recorded', helper.JobStats.test_fail_count),
            ('tests skipped', helper.JobStats.test_skip_count)
        ]
    else:
        COUNTER_MAP = [
            ('tests succeeded', helper.JobStats.test_success_count),
            ('tests failed', helper.JobStats.test_fail_count),
            ('tests skipped', helper.JobStats.test_skip_count)
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
            'test_group_name': args.test_group_name,
            'live_mode': args.live_mode,
            'test_name': args.test_name
        }

        if not config['test_group_name'] and config['test_name']:
            raise AssertionError('You must specify the test group name if test name is provided.')

        test_set = TestSuite(args.config_filename, config)
        test_set.run()

        log_test_set_summary(args.live_mode)

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
