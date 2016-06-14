import logging
from umapi import Action
from umapi.error import UMAPIRequestError


def process_rules(api, org_id, directory_users, adobe_users, rules):
    """
    Process group mapping rules

    Compares directory users with Adobe users, and decides which to add, remove, or update.

    :param api: UMAPI interface object
    :param org_id: Adobe Organization ID
    :param directory_users: List of Directory Users (provided by input.from_csv or input.from_ldap)
    :param adobe_users: List of Adobe users from UMAPI
    :param rules: List of group config rules (from group config file)
    :return: None
    """
    directory_users = list(directory_users)
    for dir_user in directory_users:
        # if the directory user does not exist in dashboard, we might add them
        if dir_user['email'] not in adobe_users:
            # we only add users that belong to at least one mapped group
            if not [g for g in dir_user['groups'] if g in rules]:
                continue

            # get a list of groups to add on user account creation
            add_groups = []
            for g in dir_user['groups']:
                add_groups += rules[g]

            # create user
            # we only support enterprise IDs at the moment
            logging.info("CREATE USER - %s", dir_user['email'])
            action = Action(user=dir_user['email']).do(
                createEnterpriseID={
                    "email": dir_user['email'],
                    "firstname": dir_user['firstname'],
                    "lastname": dir_user['lastname'],
                },
                add=add_groups,
            )

            try:
                res = api.action(org_id, action)
            except UMAPIRequestError as e:
                logging.warn("CREATE USER -- FAILURE - %s -- %s", dir_user['email'], e.code)
                continue

            if res['result'] == 'success':
                logging.info("CREATE USER -- SUCCESS - %s", dir_user['email'])
                logging.info("ADDED: %s", add_groups)
            else:
                logging.warn("CREATE USER -- FAILURE - %s", dir_user['email'])

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
            try:
                res = api.action(org_id, action)
            except UMAPIRequestError as e:
                logging.warn("ADD/REMOVE GROUPS -- FAILURE - %s -- %s", dir_user['email'], e.code)
                logging.warn("ADDED: %s", add_groups)
                logging.warn("REMOVED: %s", remove_groups)
                continue

            if res['result'] == 'success':
                logging.info("ADD/REMOVE GROUPS -- SUCCESS - %s", dir_user['email'])
                logging.info("ADDED: %s", add_groups)
                logging.info("REMOVED: %s", remove_groups)
            else:
                logging.warn("ADD/REMOVE GROUPS -- FAILURE - %s", dir_user['email'])
                logging.warn("ADDED: %s", add_groups)
                logging.warn("REMOVED: %s", remove_groups)

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

        try:
            res = api.action(org_id, action)
        except UMAPIRequestError as e:
            logging.warn("DISABLE USER -- FAILURE - %s -- %s", adobe_email, e.code)
            logging.warn("REMOVED: %s", remove_groups)
            continue

        if res['result'] == 'success':
            logging.info("DISABLE USER -- SUCCESS - %s", adobe_email)
            logging.info("REMOVED: %s", remove_groups)
        else:
            logging.warn("DISABLE USER -- FAILURE - %s", adobe_email)
            logging.warn("REMOVED: %s", remove_groups)

        continue
