import sys
import argparse
import config
import auth_store
import csv
import logging
import input
import connector
from umapi import UMAPI
from umapi.auth import Auth
from umapi.helper import paginate


def error_hook(exctype, value, tb):
    """Set up the Error Hook (default exception handler)"""
    logging.error('UNHANDLED ERROR %s: %s', exctype, value)


def process_args():
    """Process CLI args"""
    parser = argparse.ArgumentParser(description='Adobe Enterprise Dashboard User Management Connector')
    parser.add_argument('-i', '--infile', dest='infile', default=None,
                        help='input file - reads from stdin if this parameter is omitted')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s (version 0.5.0)')

    req_named = parser.add_argument_group('required arguments')
    req_named.add_argument('-c', '--config', dest='config_path', required=True,
                           help='API Config Path')
    req_named.add_argument('-a', '--auth-store', dest='auth_store_path', required=True,
                           help='Auth Store Path')

    return parser.parse_args()


def init_log(config):
    """Initialize the logger (logs to stdout)"""
    stringFormat = '%(asctime)s\t%(levelname)s\t%(message)s'
    logging.basicConfig(format=stringFormat,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=config['relativeFilePath'],
                        level=logging.DEBUG)
    
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter(stringFormat)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)



def main():
    # set up exception hook
    # sys.excepthook = error_hook

    # process command line args
    args = process_args()

    # initialize configurator
    conf = config.init(open(args.config_path, 'r'))
    c = conf['integration']

    # init the log
    init_log(conf['logging'])

    # initialize auth store object
    store = auth_store.init(c, args.auth_store_path)

    # initialize Auth object for API requests
    token = store.token()
    auth = Auth(c['enterprise']['api_key'], token)

    logging.info('Initialized auth token')

    api = UMAPI("https://" + c['server']['host'] + c['server']['endpoint'], auth)

    logging.info('Initialized API interface')

    directory_users = None

    if args.infile:
        logging.info('Found input file -- %s', args.infile)
        infile = open(args.infile, 'r')
        directory_users = input.from_csv(csv.DictReader(infile, delimiter='\t'))
        logging.info('Retrieved directory users from input file')

    for domain, domain_conf in conf['domains'].items():

        group_conf = domain_conf['groups']

        # read group config and convert to a dict, indexed by the directory group name
        group_config = dict([(g['directory_group'], g['dashboard_groups']) for g in group_conf])

        logging.info('Group config initialized')

        logging.info('Processing users for domain %s', domain)
        # if LDAP config is provided, use that even if CSV input is provided
        if not directory_users:
            logging.info('No input file specified, using LDAP config')
            lc = domain_conf['ldap']
            ldap_con = input.make_ldap_con(lc['host'], lc['username'], lc['pw'], lc['require_tls_cert'])
            directory_users = input.from_ldap(ldap_con, domain, group_config.keys(), lc['base_dn'], lc['fltr'])
            logging.info('Retrieved directory users from LDAP')

        # get all users for Adobe organization and convert to dict indexed by email address
        adobe_users = dict([(u['email'], u)
                            for u in paginate(api.users, c['enterprise']['org_id'])
                            if u['type'] == domain_conf['type']])

        if 'debug_filter' in domain_conf and domain_conf['debug_filter']:
            adobe_users = dict([(email, u) for email, u in adobe_users.items()
                                if email in domain_conf['debug_filter']])
            directory_users = [u for u in directory_users if u['email'] in domain_conf['debug_filter']]

        logging.info('Retrieved Adobe users from UMAPI')

        connector.process_rules(api, c['enterprise']['org_id'],
                                directory_users, adobe_users, group_config, domain_conf['type'])

        logging.info('Processed users for domain %s', domain)

    logging.info('Finished processing')

if __name__ == '__main__':
    main()
