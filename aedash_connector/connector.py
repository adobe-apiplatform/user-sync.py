from umapi import Action
from umapi.error import UMAPIRequestError


def process_rules(api, org_id, directory_users, adobe_users, rules):
    for dir_user in directory_users:
        if dir_user['email'] not in adobe_users:
            # create user
            print "CREATE USER - %s" % dir_user['email']
            action = Action(user=dir_user['email']).do(
                addAdobeID={"email": dir_user['email']}
            )
            try:
                res = api.action(org_id, action)
            except UMAPIRequestError as e:
                print "CREATE USER -- FAILURE - %s -- %s" % (dir_user['email'], e.code)
                continue

            if res['result'] == 'success':
                print "CREATE USER -- SUCCESS - %s" % dir_user['email']
            else:
                print "CREATE USER -- FAILURE - %s" % dir_user['email']

            continue

        if dir_user['disable']:
            # disable user
            action = Action(user=dir_user['email']).do(
                removeFromOrg={}
            )
            try:
                res = api.action(org_id, action)
            except UMAPIRequestError as e:
                print "REMOVE USER -- FAILURE - %s -- %s" % (dir_user['email'], e.code)
                continue

            if res['result'] == 'success':
                print "REMOVE USER -- SUCCESS - %s" % dir_user['email']
            else:
                print "REMOVE USER -- FAILURE - %s" % dir_user['email']

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

