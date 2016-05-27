import sys
import argparse
import config
import auth_store
import csv
import input
import connector
from umapi import UMAPI
from umapi.auth import Auth
from umapi.helper import paginate


def process_args():
    parser = argparse.ArgumentParser(description='Prototype Adobe Enterprise Dashboard User Management Connector')
    parser.add_argument('--example-config', dest='example_config', action='store_const',
                        const=config.example_config, default=None,
                        help='generate example config file and exit')
    parser.add_argument('--config-path', dest='config_path', default=None,
                        help='API Config Path')
    parser.add_argument('--group-config', dest='group_config', default=None,
                        help='Group Config Path')
    parser.add_argument('--ldap-config', dest='ldap_config', default=None,
                        help='LDAP Config Path')
    parser.add_argument('--auth-store-path', dest='auth_store_path', default=None,
                        help='Auth Store Path')
    parser.add_argument('--infile', dest='infile', default=None,
                        help='input file - reads from stdin if this parameter is omitted')

    return parser.parse_args()


def main():
    # process command line args
    args = process_args()

    if args.example_config:
        print args.example_config()
        sys.exit()

    # initialize configurator
    c = config.init(open(args.config_path, 'r'))
    store = auth_store.init(c, args.auth_store_path)
    token = store.token()
    auth = Auth(c['enterprise']['api_key'], token)

    api = UMAPI("https://" + c['server']['host'] + c['server']['endpoint'], auth)

    if args.ldap_config:
        lc = config.ldap_config(open(args.ldap_config, 'r'))
        directory_users = input.from_ldap(lc['host'], lc['username'], lc['pw'])
    else:
        if args.infile:
            infile = open(args.infile, 'r')
        else:
            infile = sys.stdin

        directory_users = input.from_csv(csv.DictReader(infile, delimiter='\t'))

    if not args.group_config:
        print "Please provide the group config path"
        sys.exit(1)

    group_config = dict([(g['directory_group'], g['dashboard_groups'])
                         for g in config.group_config(open(args.group_config, 'r'))])

    adobe_users = dict([(u['email'], u) for u in paginate(api.users, c['enterprise']['org_id'])
                        if 'adorton' in u['email']])

    connector.process_rules(api, c['enterprise']['org_id'], directory_users, adobe_users, group_config)

if __name__ == '__main__':
    main()
