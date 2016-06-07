from umapi import Action
from umapi.error import UMAPIRequestError


def process_rules(api, org_id, directory_users, adobe_users, rules):
    directory_users = list(directory_users)
    for dir_user in directory_users:
        if dir_user['email'] not in adobe_users:
            if not [g for g in dir_user['groups'] if g in rules]:
                continue

            add_groups = []
            for g in dir_user['groups']:
                add_groups += rules[g]

            # create user
            print "CREATE USER - %s" % dir_user['email']
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
                print "CREATE USER -- FAILURE - %s -- %s" % (dir_user['email'], e.code)
                continue

            if res['result'] == 'success':
                print "CREATE USER -- SUCCESS - %s" % dir_user['email']
                print "ADDED: ", add_groups
            else:
                print "CREATE USER -- FAILURE - %s" % dir_user['email']

            continue

        # if user exists and does not need disabling, then we should check to see if we need to update
        # update user details if needed (first, last, etc)
        # compare groups and add/remove where necessary

        # skipping user update until we get a dashboard

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
                print "ADD/REMOVE GROUPS -- FAILURE - %s -- %s" % (dir_user['email'], e.code)
                print "ADDED: ", add_groups
                print "REMOVED: ", remove_groups
                continue

            if res['result'] == 'success':
                print "ADD/REMOVE GROUPS -- SUCCESS - %s" % dir_user['email']
                print "ADDED: ", add_groups
                print "REMOVED: ", remove_groups
            else:
                print "ADD/REMOVE GROUPS -- FAILURE - %s" % dir_user['email']
                print "ADDED: ", add_groups
                print "REMOVED: ", remove_groups

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
            print "DISABLE USER -- FAILURE - %s -- %s" % (adobe_email, e.code)
            print "REMOVED: ", remove_groups
            continue

        if res['result'] == 'success':
            print "DISABLE USER -- SUCCESS - %s" % adobe_email
            print "REMOVED: ", remove_groups
        else:
            print "DISABLE USER -- FAILURE - %s" % adobe_email
            print "REMOVED: ", remove_groups

        continue
