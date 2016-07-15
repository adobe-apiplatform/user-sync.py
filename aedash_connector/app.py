import sys
import argparse
import config
import csv
import logging
import input
import connector
from umapi import UMAPI
from umapi.auth import Auth, JWT, AccessRequest
from umapi.helper import paginate


def error_hook(exctype, value, tb):
    """Set up the Error Hook (default exception handler)"""
    logging.error('UNHANDLED ERROR %s: %s', exctype, value)


def process_args():
    """Process CLI args"""
    parser = argparse.ArgumentParser(description='Adobe Enterprise Dashboard User Management Connector')
    parser.add_argument('-i', '--infile', dest='infile', default=None,
                        help='input file - reads from stdin if this parameter is omitted')
    parser.add_argument('-t', '--test-mode', dest='test_mode', action='store_true',
                        help='run API action calls in test mode (does not execute changes)')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s (version 0.5.0)')
    parser.set_defaults(test_mode=False)

    req_named = parser.add_argument_group('required arguments')
    req_named.add_argument('-c', '--config', dest='config_path', required=True,
                           help='API Config Path')

    return parser.parse_args()


def init_log(config):
    """Initialize the logger (logs to stdout)"""
    stringFormat = '%(asctime)s\t%(levelname)s\t%(message)s'
    
    def levelLookup(x):
        return {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }[x]
        
    loggingLevel = levelLookup(config['level']) or logging.NOTSET
        
    logging.basicConfig(format=stringFormat,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=config['relativeFilePath'],
                        level=loggingLevel)
    
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

    # the JWT object build the JSON Web Token
    jwt = JWT(
        c['enterprise']['org_id'],
        c['enterprise']['tech_acct'],
        c['server']['ims_host'],
        c['enterprise']['api_key'],
        open(c['enterprise']['priv_key_path'], 'r')
    )

    # when called, the AccessRequest object retrieves an access token from IMS
    access_req = AccessRequest(
        "https://" + c['server']['ims_host'] + c['server']['ims_endpoint_jwt'],
        c['enterprise']['api_key'],
        c['enterprise']['client_secret'],
        jwt()
    )

    # initialize Auth object for API requests
    auth = Auth(c['enterprise']['api_key'], access_req())

    logging.info('Initialized auth token')

    api = UMAPI("https://" + c['server']['host'] + c['server']['endpoint'], auth, args.test_mode)

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
