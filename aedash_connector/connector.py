import logging
import email.utils
import time
import math
import random
from umapi import Action
from umapi.error import UMAPIError, UMAPIRetryError, UMAPIRequestError


def process_rules(api, org_id, directory_users, adobe_users, rules, type):
    """
    Process group mapping rules

    Compares directory users with Adobe users, and decides which to add, remove, or update.

    :param api: UMAPI interface object
    :param org_id: Adobe Organization ID
    :param directory_users: List of Directory Users (provided by input.from_csv or input.from_ldap)
    :param adobe_users: List of Adobe users from UMAPI
    :param rules: List of group config rules (from group config file)
    :param type: Identity type - federatedID or enterpriseID
    :return: None
    """
    directory_users = list(directory_users)

    manager = ActionManager(api, org_id)

    for dir_user in directory_users:
        # if the directory user does not exist in dashboard, we might add them
        if dir_user['email'] not in adobe_users:
            # we only add users that belong to at least one mapped group
            if not [g for g in dir_user['groups'] if g in rules]:
                continue

            # get a list of groups to add on user account creation
            add_groups = []
            for g in dir_user['groups']:
                if g in rules:
                    add_groups += rules[g]

            # create user
            # we only support enterprise IDs at the moment
            logging.info("CREATE USER - %s", dir_user['email'])

            if type == 'federatedID':
                action = Action(user=dir_user['email']).do(
                    createFederatedID={
                        "email": dir_user['email'],
                        "firstname": dir_user['firstname'],
                        "lastname": dir_user['lastname'],
                        "country": dir_user['country'],
                    },
                    add=add_groups,
                )
            else:
                action = Action(user=dir_user['email']).do(
                    createEnterpriseID={
                        "email": dir_user['email'],
                        "firstname": dir_user['firstname'],
                        "lastname": dir_user['lastname'],
                    },
                    add=add_groups,
                )

            manager.add_action(action)

            continue

        # if user exists and does not need disabling, then we should check to see if we need to update
        # update user details if needed (first, last, etc)
        # compare groups and add/remove where necessary

        add_groups = []
        remove_groups = []
        adobe_user = adobe_users[dir_user['email']]

        # get adobe groups that user currently belongs to
        if 'groups' not in adobe_user:
            adobe_membership = []
        else:
            adobe_membership = adobe_user['groups']

        dir_membership = []
        for g in dir_user['groups']:
            if g in rules:
                dir_membership += rules[g]

        add_groups += [g for g in dir_membership if g not in adobe_membership]
        remove_groups += [g for g in adobe_membership if g not in dir_membership]

        do_params = {}
        if add_groups:
            do_params['add'] = add_groups

        if remove_groups:
            do_params['remove'] = remove_groups

        if do_params:
            action = Action(user=dir_user['email']).do(
                **do_params
            )
            manager.add_action(action)
            logging.info("ADD/REMOVE GROUPS -- SUCCESS - %s", dir_user['email'])
            logging.info("ADDED: %s", add_groups)
            logging.info("REMOVED: %s", remove_groups)

    # check for accounts to disable (remove group membership)
    # get a list of directory email addresses
    dir_emails = [u['email'] for u in directory_users]
    adobe_groups = []
    for groups in rules.values():
        adobe_groups += groups
    for adobe_email, adobe_user in adobe_users.items():
        # don't disable if adobe email is found in directory
        if adobe_email in dir_emails:
            continue

        if 'groups' not in adobe_user:
            continue

        # only remove users that belong to at least one directory group
        remove_groups = [g for g in adobe_user['groups'] if g in adobe_groups]

        if not remove_groups:
            continue

        action = Action(user=adobe_email).do(
            remove=adobe_user['groups']
        )

        manager.add_action(action)

        logging.info("DISABLE USER --  %s", adobe_email)
        logging.info("REMOVING: %s", remove_groups)

        continue

    if manager.actions:
        manager.execute()


class ActionManager(object):
    max_actions = 10

    def __init__(self, api, org_id):
        self.actions = []
        self.api = api
        self.org_id = org_id

    def add_action(self, action):
        self.actions.append(action)
        if len(self.actions) >= self.max_actions:
            self.execute()
            self.actions = []

    def execute(self):
        num_attempts = 0
        num_attempts_max = 4
        backoff_exponential_factor = 15  # seconds
        backoff_random_delay_max = 5  # seconds

        while True:
            num_attempts += 1

            if num_attempts > num_attempts_max:
                logging.warn("ACTION FAILURE NO MORE RETRIES, SKIPPING...")
                break

            try:
                res = self.api.action(self.org_id, self.actions)
            except UMAPIRequestError as e:
                logging.warn("ACTION ERROR - %s", e.code)
                break
            except UMAPIRetryError as e:
                logging.warn("ACTION FAILURE -- %s - RETRYING", e.res.status_code)
                if "Retry-After" in e.res.headers:
                    retry_after_date = email.utils.parsedate_tz(e.res.headers["Retry-After"])
                    if retry_after_date is not None:
                        # header contains date
                        time_backoff = int(email.utils.mktime_tz(retry_after_date) - time.time())
                    else:
                        # header contains delta seconds
                        time_backoff = int(e.res.headers["Retry-After"])
                else:
                    # use exponential backoff with random delayh
                    time_backoff = int(math.pow(2, num_attempts - 1)) * \
                                   backoff_exponential_factor + \
                                   random.randint(0, backoff_random_delay_max)

                logging.info("Retrying in " + str(time_backoff) + " seconds...")
                time.sleep(time_backoff)
                continue
            except UMAPIError as e:
                logging.warn("ACTION ERROR -- %s - %s", e.res.status_code, e.res.text)
                break

            if res['result'] == 'success' and not res['notCompleted']:
                logging.debug('ACTION SUCCESS -- %d completed', res['completed'])
                break
            elif res['result'] == 'success':
                logging.warn('ACTION PARTIAL SUCCESS -- %d completed, %d failed', res['completed'], res['incomplete'])
                break
            else:
                logging.warn("ACTION FAILURE")
                break
