# Copyright (c) 2016-2017 Adobe Systems Incorporated.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import csv
import logging

import user_sync.connector.umapi
import user_sync.error
import user_sync.helper
import user_sync.identity_type

GROUP_NAME_DELIMITER = '::'
PRIMARY_UMAPI_NAME = None

class RuleProcessor(object):
    
    def __init__(self, caller_options):
        '''
        :type caller_options:dict
        '''        
        options = {
            # these are in alphabetical order!  Always add new ones that way!
            'after_mapping_hook': None,
            'default_country_code': None,
            'delete_strays': False,
            'directory_group_filter': None,
            'directory_group_mapped': False,
            'disentitle_strays': False,
            'exclude_groups': [],
            'exclude_identity_types': [],
            'exclude_strays': False,
            'exclude_users': [],
            'extended_attributes': None,
            'manage_groups': False,
            'max_adobe_only_users': 200,
            'new_account_type': user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE,
            'remove_strays': False,
            'stray_list_input_path': None,
            'stray_list_output_path': None,
            'test_mode': False,
            'update_user_info': True,
            'username_filter_regex': None,
        }
        options.update(caller_options)        
        self.options = options        
        self.directory_user_by_user_key = {}
        self.filtered_directory_user_by_user_key = {}
        self.umapi_info_by_name = {}
        # counters for action summary log
        self.action_summary = {
            # these are in alphabetical order!  Always add new ones that way!
            'adobe_strays_processed': 0,
            'adobe_users_created': 0,
            'adobe_users_excluded': 0,
            'adobe_users_read': 0,
            'adobe_users_unchanged': 0,
            'adobe_users_updated': 0,
            'directory_users_read': 0,
            'directory_users_selected': 0,
        }
        self.logger = logger = logging.getLogger('processor')

        # save away the exclude options for use in filtering
        self.exclude_groups = self.normalize_groups(options['exclude_groups'])
        self.exclude_identity_types = options['exclude_identity_types']
        self.exclude_users = options['exclude_users']

        # There's a big difference between how we handle the primary umapi,
        # and how we handle secondary umapis.  We care about all the (non-excluded)
        # users in the primary umapi, but we only care about those users in the
        # secondary umapis that match (non-excluded) users in the primary umapi.
        # That's because all we do in the secondary umapis is group management
        # of primary-umapi users, who are presumed to be in primary-umapi domains.
        # So instead of keeping track of excluded users in the primary umapi,
        # we keep track of included users, so we can match them against users
        # in the secondary umapis (and exclude all that don't match).  Finally,
        # we keep track of user keys (in any umapi) that we have updated, so
        # we can correctly report their count.
        self.adobe_user_count = 0
        self.included_user_keys = set()
        self.excluded_user_count = 0
        self.updated_user_keys = set()

        # stray key input path comes in, stray_list_output_path goes out
        self.stray_key_map = self.make_stray_key_map()
        if options['stray_list_input_path']:
            self.read_stray_key_map(options['stray_list_input_path'])
        self.stray_list_output_path = options['stray_list_output_path']
        
        # determine what processing is needed on strays
        self.will_manage_strays = (options['manage_groups'] or options['disentitle_strays'] or
                                   options['remove_strays'] or options['delete_strays'])
        self.will_process_strays = (not options['exclude_strays']) and (options['stray_list_output_path'] or
                                                                        self.will_manage_strays)

        # in/out variables for per-user after-mapping-hook code
        self.after_mapping_hook_scope = {
            'source_attributes': None,          # in: attributes retrieved from customer directory system (eg 'c', 'givenName')
                                                # out: N/A
            'source_groups': None,              # in: customer-side directory groups found for user
                                                # out: N/A
            'target_attributes': None,          # in: user's attributes for UMAPI calls as defined by usual rules (eg 'country', 'firstname')
                                                # out: user's attributes for UMAPI calls as potentially changed by hook code
            'target_groups': None,              # in: adobe groups mapped for user by usual rules
                                                # out: adobe groups as potentially changed by hook code
            'logger': logger,                   # make loging available to hook code
            'hook_storage': None,               # for exclusive use by hook code; persists across calls
        }

        if logger.isEnabledFor(logging.DEBUG):
            options_to_report = options.copy()
            username_filter_regex = options_to_report['username_filter_regex']
            if username_filter_regex is not None:
                options_to_report['username_filter_regex'] = "%s: %s" % (type(username_filter_regex), username_filter_regex.pattern)
            logger.debug('Initialized with options: %s', options_to_report)

    def run(self, directory_groups, directory_connector, umapi_connectors):
        '''
        :type directory_groups: dict(str, list(AdobeGroup)
        :type directory_connector: user_sync.connector.directory.DirectoryConnector
        :type umapi_connectors: UmapiConnectors
        '''
        logger = self.logger

        self.prepare_umapi_infos()

        if directory_connector is not None:
            load_directory_stats = user_sync.helper.JobStats("Load from Directory", divider = "-")
            load_directory_stats.log_start(logger)
            self.read_desired_user_groups(directory_groups, directory_connector)
            load_directory_stats.log_end(logger)
            should_sync_umapi_users = True
        else:
            # no directory users to sync with
            should_sync_umapi_users = False
        
        umapi_stats = user_sync.helper.JobStats("Sync Umapi", divider = "-")
        umapi_stats.log_start(logger)
        if should_sync_umapi_users:
            self.process_umapi_users(umapi_connectors)
        if self.will_process_strays:
            self.process_strays(umapi_connectors)
        umapi_connectors.execute_actions()
        umapi_stats.log_end(logger)
        self.log_action_summary(umapi_connectors)
            
    def log_action_summary(self, umapi_connectors):
        '''
        log number of affected directory and Adobe users,
        and a summary of network actions sent and that had errors
        :type umapi_connectors: UmapiConnectors
        :return: None
        '''
        logger = self.logger
        # find the total number of directory users and selected/filtered users
        self.action_summary['directory_users_read'] = len(self.directory_user_by_user_key)
        self.action_summary['directory_users_selected'] = len(self.filtered_directory_user_by_user_key)
        # find the total number of adobe users and excluded users
        self.action_summary['adobe_users_read'] = self.adobe_user_count
        self.action_summary['adobe_users_excluded'] = self.excluded_user_count
        self.action_summary['adobe_users_updated'] = len(self.updated_user_keys)
        # find out the number of users that have no changes; this depends on whether
        # we actually read the directory or read an input file.  So there are two cases:
        if self.action_summary['adobe_users_read'] == 0:
            self.action_summary['adobe_users_unchanged'] = 0
        else:
            self.action_summary['adobe_users_unchanged'] = (
                self.action_summary['adobe_users_read'] -
                self.action_summary['adobe_users_excluded'] -
                self.action_summary['adobe_users_updated'] -
                self.action_summary['adobe_strays_processed']
            )
        if self.options['test_mode']:
            header = '- Action Summary (TEST MODE) -'
        else:
            header = '------- Action Summary -------'
        logger.info('---------------------------' + header + '---------------------------')

        # English text description for action summary log.
        # The action summary will be shown the same order as they are defined in this list
        action_summary_description = [
            ['directory_users_read', 'Number of directory users read'],
            ['directory_users_selected', 'Number of directory users selected for input'],
            ['adobe_users_read', 'Number of Adobe users read'],
            ['adobe_users_excluded', 'Number of Adobe users excluded from updates'],
            ['adobe_users_unchanged', 'Number of non-excluded Adobe users with no changes'],
            ['adobe_users_created', 'Number of new Adobe users added'],
            ['adobe_users_updated', 'Number of matching Adobe users updated'],
        ]
        if self.will_process_strays:
            if self.options['delete_strays']:
                action = 'deleted'
            elif self.options['remove_strays']:
                action = 'removed'
            elif self.options['disentitle_strays']:
                action = 'removed from all groups'
            else:
                action = 'with groups processed'
            action_summary_description.append(['adobe_strays_processed', 'Number of Adobe-only users ' + action])

        # prepare the network summary
        umapi_summary_format = 'Number of%s%s UMAPI actions sent (total, success, error)'
        if umapi_connectors.get_secondary_connectors():
            spacer = ' '
            connectors = [('primary', umapi_connectors.get_primary_connector())]
            connectors.extend(umapi_connectors.get_secondary_connectors().iteritems())
        else:
            spacer = ''
            connectors = [('', umapi_connectors.get_primary_connector())]

        # to line up the stats, we pad them out to the longest stat description length,
        # so first we compute that pad length
        pad = 0
        for action_description in action_summary_description:
            if len(action_description[1]) > pad:
                pad = len(action_description[1])
        for name, _ in connectors:
            umapi_summary_description = umapi_summary_format % (spacer, name)
            if len(umapi_summary_description) > pad:
                pad = len(umapi_summary_description)
        # and then we use it
        for action_description in action_summary_description:
            description = action_description[1].rjust(pad, ' ')
            action_count = self.action_summary[action_description[0]]
            logger.info('  %s: %s', description, action_count)
        for name, umapi_connector in connectors:
            sent, errors = umapi_connector.get_action_manager().get_statistics()
            description = (umapi_summary_format % (spacer, name)).rjust(pad, ' ')
            logger.info('  %s: (%s, %s, %s)', description, sent, sent - errors, errors)
        logger.info('------------------------------------------------------------------------------------')

    def will_manage_groups(self):
        return self.options['manage_groups']
    
    def get_umapi_info(self, umapi_name):
        umapi_info = self.umapi_info_by_name.get(umapi_name)
        if umapi_info is None:
            self.umapi_info_by_name[umapi_name] = umapi_info = UmapiTargetInfo(umapi_name)
        return umapi_info
    
    def prepare_umapi_infos(self):
        '''
        Make sure we have prepared organizations for all the mapped groups, including extensions.
        '''
        for adobe_group in AdobeGroup.iter_groups():
            umapi_info = self.get_umapi_info(adobe_group.get_umapi_name())
            umapi_info.add_mapped_group(adobe_group.get_group_name())

    def read_desired_user_groups(self, mappings, directory_connector):
        '''
        :type mappings: dict(str, list(AdobeGroup))
        :type directory_connector: user_sync.connector.directory.DirectoryConnector
        '''
        self.logger.debug('Building work list...')
                
        options = self.options
        directory_group_filter = options['directory_group_filter']
        if directory_group_filter is not None:
            directory_group_filter = set(directory_group_filter)
        extended_attributes = options.get('extended_attributes')
        
        directory_user_by_user_key = self.directory_user_by_user_key        
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key

        directory_groups = set(mappings.iterkeys())
        if directory_group_filter is not None:
            directory_groups.update(directory_group_filter)
        directory_users = directory_connector.load_users_and_groups(directory_groups, extended_attributes)

        for directory_user in directory_users:
            user_key = self.get_directory_user_key(directory_user)
            directory_user_by_user_key[user_key] = directory_user            
            
            if not self.is_directory_user_in_groups(directory_user, directory_group_filter):
                continue
            if not self.is_selected_user_key(user_key):
                continue

            filtered_directory_user_by_user_key[user_key] = directory_user
            self.get_umapi_info(PRIMARY_UMAPI_NAME).add_desired_group_for(user_key, None)

            # set up groups in hook scope; the target groups will be used whether or not there's customer hook code
            self.after_mapping_hook_scope['source_groups'] = set()
            self.after_mapping_hook_scope['target_groups'] = set()
            for group in directory_user['groups']:
                self.after_mapping_hook_scope['source_groups'].add(group) # this is a directory group name
                adobe_groups = mappings.get(group)
                if adobe_groups is not None:
                    for adobe_group in adobe_groups:
                        self.after_mapping_hook_scope['target_groups'].add(adobe_group.get_qualified_name())

            # only if there actually is hook code: set up rest of hook scope, invoke hook, update user attributes
            if options['after_mapping_hook'] is not None:
                self.after_mapping_hook_scope['source_attributes'] = directory_user['source_attributes'].copy()

                target_attributes = dict()
                target_attributes['email'] = directory_user.get('email')
                target_attributes['username'] = directory_user.get('username')
                target_attributes['domain'] = directory_user.get('domain')
                target_attributes['firstname'] = directory_user.get('firstname')
                target_attributes['lastname'] = directory_user.get('lastname')
                target_attributes['country'] = directory_user.get('country')
                target_attributes['uid'] = directory_user.get('uid')
                self.after_mapping_hook_scope['target_attributes'] = target_attributes

                # invoke the customer's hook code
                self.log_after_mapping_hook_scope(before_call=True)
                exec(options['after_mapping_hook'], self.after_mapping_hook_scope)
                self.log_after_mapping_hook_scope(after_call=True)

                # copy modified attributes back to the user object
                directory_user.update(self.after_mapping_hook_scope['target_attributes'])

            for target_group_qualified_name in self.after_mapping_hook_scope['target_groups']:
                target_group = AdobeGroup.lookup(target_group_qualified_name)
                if target_group is not None:
                    umapi_info = self.get_umapi_info(target_group.get_umapi_name())
                    umapi_info.add_desired_group_for(user_key, target_group.get_group_name())
                else:
                    self.logger.error('Target adobe group %s is not known; ignored', target_group_qualified_name)

        self.logger.debug('Total directory users after filtering: %d', len(filtered_directory_user_by_user_key))
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('Group work list: %s', dict([(umapi_name, umapi_info.get_desired_groups_by_user_key())
                                                           for umapi_name, umapi_info
                                                           in self.umapi_info_by_name.iteritems()]))
    
    def is_directory_user_in_groups(self, directory_user, groups):
        '''
        :type directory_user: dict
        :type groups: set
        :rtype bool
        '''
        if groups == None:
            return True
        for directory_user_group in directory_user['groups']:
            if directory_user_group in groups:
                return True
        return False
    
    def process_umapi_users(self, umapi_connectors):
        '''
        This is where we actually "do the sync"; that is, where we match users on the two sides.
        When we get here, we have loaded all the directory users *and* we have loaded all the adobe users,
        and (conceptually) we match them up, updating the adobe users that match, marking the umapi
        users that don't match for deletion, and adding adobe users for the directory users that didn't match.
        What makes the code here more complex is that, instead of looping over users just once and
        updating each user in all of the umapi connectors at that time, we instead loop over users
        once per umapi for which we have a umapi connector, and we do the matching logic for each of
        those umapis.
        :type umapi_connectors: UmapiConnectors
        '''        
        manage_groups = self.will_manage_groups()

        if umapi_connectors.get_secondary_connectors():
            self.logger.debug('Syncing users to primary umapi...')
        else:
            self.logger.debug('Syncing users to umapi...')
        primary_umapi_info = self.get_umapi_info(PRIMARY_UMAPI_NAME)

        # Loop over users and compare then and process differences
        primary_adds_by_user_key = self.update_umapi_users_for_connector(primary_umapi_info,
                                                                         umapi_connectors.get_primary_connector())

        # Handle creates for new users.  This also drives adding the new user to the secondaries,
        # but the secondary adobe groups will be managed below in the usual way.
        for user_key, groups_to_add in primary_adds_by_user_key.iteritems():
            self.add_umapi_user(user_key, groups_to_add, umapi_connectors)
        # we just did a bunch of adds, we need to flush the connections before we can sync groups
        umapi_connectors.execute_actions()

        # Now manage the adobe groups in the secondaries
        for umapi_name, umapi_connector in umapi_connectors.get_secondary_connectors().iteritems():
            secondary_umapi_info = self.get_umapi_info(umapi_name)
            if len(secondary_umapi_info.get_mapped_groups()) == 0:
                continue
            self.logger.debug('Syncing users to secondary umapi %s...', umapi_name)
            secondary_updates_by_user_key = self.update_umapi_users_for_connector(secondary_umapi_info, umapi_connector)
            if secondary_updates_by_user_key:
                self.logger.critical("Shouldn't happen! In secondary umapi %s, the following users were not found: %s",
                                     umapi_name, secondary_updates_by_user_key.keys())

    def is_selected_user_key(self, user_key):
        '''
        :type user_key: str
        '''
        username_filter_regex = self.options['username_filter_regex']
        if username_filter_regex is not None:
            username = self.get_username_from_user_key(user_key)
            search_result = username_filter_regex.search(username)
            if search_result is None:
                return False
        return True

    def make_stray_key_map(self):
        '''
        The stray key map is a two-level map:
        * the first level maps umapis to user_keys of users in those umapis;
        * the second level maps those user_keys to the groups that should be removed from them.
        :return: dict whose values are dicts
        '''
        return {}

    def get_stray_keys(self, umapi_name=PRIMARY_UMAPI_NAME):
        return self.stray_key_map.get(umapi_name, {})

    def add_stray(self, umapi_name, user_key, removed_groups=None):
        '''
        Remember that this user is a stray found in this umapi connector.  The special marker value None
        means that we are about to start processing this connector, so initialize the map for it.
        :param umapi_name: name of the umapi connector the user was found in
        :param user_key: user_key (str) from a user in that connector
        :param removed_groups: a set of adobe_groups to be removed from the user in that umapi
        '''
        if user_key is None:
            if umapi_name not in self.stray_key_map:
                self.stray_key_map[umapi_name] = {}
        else:
            self.stray_key_map[umapi_name][user_key] = removed_groups

    def process_strays(self, umapi_connectors):
        '''
        Do the top-level logic for stray processing (output to file or clean them up), enforce limits, etc.
        The actual work is done in sub-functions that we call.
        :param umapi_connectors:
        :return:
        '''
        stray_count = len(self.get_stray_keys())
        if self.stray_list_output_path:
            self.write_stray_key_map()
        if self.will_manage_strays:
            max_missing = self.options['max_adobe_only_users']
            if stray_count > max_missing:
                self.logger.critical('Unable to process Adobe-only users, as their count (%s) is larger '
                                     'than the max_adobe_only_users setting (%d)', stray_count, max_missing)
                self.action_summary['adobe_strays_processed'] = 0
                return
            self.action_summary['adobe_strays_processed'] = stray_count
            self.logger.debug("Processing Adobe-only users...")
            self.manage_strays(umapi_connectors)
                    
    def manage_strays(self, umapi_connectors):
        '''
        Manage strays.  This doesn't require having loaded users from the umapi.
        Management of groups, removal of entitlements and removal from umapi are 
        processed against every secondary umapi, whereas account deletion is only done
        against the primary umapi.
        :type umapi_connectors: UmapiConnectors
        '''
        # figure out what management to do
        manage_stray_groups = self.will_manage_groups()
        disentitle_strays = self.options['disentitle_strays']
        remove_strays = self.options['remove_strays']
        delete_strays = self.options['delete_strays']

        # all our processing is controlled by the strays in the primary organization
        primary_strays = self.get_stray_keys()

        # convenience function to get umapi Commands given a user key
        def get_commands(user_key):
            '''Given a user key, returns the umapi commands targeting that user'''
            id_type, username, domain = self.parse_user_key(user_key)
            return user_sync.connector.umapi.Commands(identity_type=id_type, username=username, domain=domain)

        # do the secondary umapis first, in case we are deleting user accounts from the primary umapi at the end
        for umapi_name, umapi_connector in umapi_connectors.get_secondary_connectors().iteritems():
            secondary_strays = self.get_stray_keys(umapi_name)
            for user_key in primary_strays:
                if user_key in secondary_strays:
                    commands = get_commands(user_key)
                    if disentitle_strays:
                        self.logger.info('Removing all adobe groups in %s for Adobe-only user: %s',
                                         umapi_name, user_key)
                        commands.remove_all_groups()
                    elif remove_strays or delete_strays:
                        self.logger.info('Removing Adobe-only user from %s: %s',
                                         umapi_name, user_key)
                        commands.remove_from_org(False)
                    elif manage_stray_groups:
                        groups_to_remove = secondary_strays[user_key]
                        if groups_to_remove:
                            self.logger.info('Removing mapped groups in %s from Adobe-only user: %s',
                                             umapi_name, user_key)
                            commands.remove_groups(groups_to_remove)
                        else:
                            continue
                    else:
                        # haven't done anything, don't send commands
                        continue
                    umapi_connector.send_commands(commands)
            # make sure the commands for each umapi are executed before moving to the next
            umapi_connector.get_action_manager().flush()

        # finish with the primary umapi
        primary_connector = umapi_connectors.get_primary_connector()
        for user_key in primary_strays:
            commands = get_commands(user_key)
            if disentitle_strays:
                self.logger.info('Removing all adobe groups for Adobe-only user: %s', user_key)
                commands.remove_all_groups()
            elif remove_strays or delete_strays:
                action = "Deleting" if delete_strays else "Removing"
                self.logger.info('%s Adobe-only user: %s', action, user_key)
                commands.remove_from_org(True if delete_strays else False)
            elif manage_stray_groups:
                groups_to_remove = primary_strays[user_key]
                if groups_to_remove:
                    self.logger.info('Removing mapped groups from Adobe-only user: %s', user_key)
                    commands.remove_groups(groups_to_remove)
                else:
                    continue
            else:
                # haven't done anything, don't send commands
                continue
            primary_connector.send_commands(commands)
        # make sure the actions get sent
        primary_connector.get_action_manager().flush()

    def get_user_attributes(self, directory_user):
        attributes = {}
        attributes['email'] = directory_user['email']
        attributes['firstname'] = directory_user['firstname']
        attributes['lastname'] = directory_user['lastname']
        return attributes
    
    def get_identity_type_from_directory_user(self, directory_user):
        identity_type = directory_user.get('identity_type')
        if identity_type is None:
            identity_type = self.options['new_account_type']
            self.logger.warning('Found user with no identity type, using %s: %s', identity_type, directory_user)
        return identity_type

    def get_identity_type_from_umapi_user(self, umapi_user):
        identity_type = umapi_user.get('type')
        if identity_type is None:
            identity_type = self.options['new_account_type']
            self.logger.error('Found adobe user with no identity type, using %s: %s', identity_type, umapi_user)
        return identity_type

    def create_commands_from_directory_user(self, directory_user, identity_type = None):
        '''
        :type directory_user: dict
        :type identity_type: str
        '''
        if identity_type is None:
            identity_type = self.get_identity_type_from_directory_user(directory_user)
        commands = user_sync.connector.umapi.Commands(identity_type, directory_user['email'],
                                                      directory_user['username'], directory_user['domain'])
        return commands
    
    def add_umapi_user(self, user_key, groups_to_add, umapi_connectors):
        '''
        Add the user to the primary umapi with groups, and create in group-using secondaries without groups.  
        The secondary group mappings should be taken care of by caller when the secondaries are walked.
        :type user_key: str
        :type umapi_connectors: UmapiConnectors
        '''
        # Check to see what we're updating
        options = self.options
        update_user_info = options['update_user_info'] 
        manage_groups = self.will_manage_groups()

        # put together the user's attributes
        directory_user = self.directory_user_by_user_key[user_key]
        identity_type = self.get_identity_type_from_directory_user(directory_user)
        primary_commands = self.create_commands_from_directory_user(directory_user, identity_type)
        attributes = self.get_user_attributes(directory_user)
        # check whether the country is set in the directory, use default if not
        country = directory_user['country']
        if not country:
            country = options['default_country_code']
        if not country:
            if identity_type == user_sync.identity_type.ENTERPRISE_IDENTITY_TYPE:
                # Enterprise users are allowed to have undefined country
                country = 'UD'
            else:
                self.logger.error("User %s cannot be added as it has a blank country code"
                                  " and no default has been specified.", user_key)
                return
        attributes['country'] = country
        if attributes.get('firstname') is None:
            attributes.pop('firstname', None)
        if attributes.get('lastname') is None:
            attributes.pop('lastname', None)
        attributes['option'] = "updateIfAlreadyExists" if update_user_info else 'ignoreIfAlreadyExists'

        # add the user to primary with groups
        self.logger.info('Adding directory user with user key: %s', user_key)
        self.action_summary['adobe_users_created'] += 1
        primary_commands.add_user(attributes)
        if manage_groups:
            primary_commands.add_groups(groups_to_add)
        umapi_connectors.get_primary_connector().send_commands(primary_commands)
        # add the user to secondaries without groups
        for umapi_name, umapi_connector in umapi_connectors.secondary_connectors.iteritems():
            secondary_umapi_info = self.get_umapi_info(umapi_name)
            # only add the user to this secondary if he is in groups in this secondary
            if secondary_umapi_info.get_desired_groups(user_key):
                self.logger.info('Adding directory user to %s with user key: %s', umapi_name, user_key)
                secondary_commands = self.create_commands_from_directory_user(directory_user, identity_type)
                secondary_commands.add_user(attributes)
                umapi_connector.send_commands(secondary_commands)

    def update_umapi_user(self, umapi_info, user_key, umapi_connector,
                          attributes_to_update=None, groups_to_add=None, groups_to_remove=None,
                          umapi_user = None):
        # Note that the user may exist only in the directory, only in the umapi, or both at this point.
        # When we are updating an Adobe user who has been removed from the directory, we have to be careful to use
        # data from the umapi_user parameter and not try to get information from the directory.
        '''
        Send the action to update aspects of an adobe user, like info and groups
        :type umapi_info: UmapiTargetInfo
        :type user_key: str
        :type umapi_connector: user_sync.connector.umapi.UmapiConnector
        :type attributes_to_update: dict
        :type groups_to_add: set(str)
        :type groups_to_remove: set(str)
        :type umapi_user: dict # with type, username, domain, and email entries
        '''
        is_primary_org = umapi_info.get_name() == PRIMARY_UMAPI_NAME
        if attributes_to_update or groups_to_add or groups_to_remove:
            self.updated_user_keys.add(user_key)
        if attributes_to_update:
            self.logger.info('Updating info for user key: %s changes: %s', user_key, attributes_to_update)
        if groups_to_add or groups_to_remove:
            if is_primary_org:
                self.logger.info('Managing groups for user key: %s added: %s removed: %s',
                                 user_key, groups_to_add, groups_to_remove)
            else:
                self.logger.info('Managing groups in %s for user key: %s added: %s removed: %s',
                                 umapi_info.get_name(), user_key, groups_to_add, groups_to_remove)

        if user_key in self.directory_user_by_user_key:
            directory_user = self.directory_user_by_user_key[user_key]
            identity_type = self.get_identity_type_from_directory_user(directory_user)
        else:
            directory_user = umapi_user
            identity_type = umapi_user.get('type')

        commands = self.create_commands_from_directory_user(directory_user, identity_type=identity_type)
        if identity_type != user_sync.identity_type.ADOBEID_IDENTITY_TYPE:
            commands.update_user(attributes_to_update)
        else:
            if attributes_to_update:
                self.logger.warning("Can't update attributes on Adobe ID user: %s", umapi_user.get("email"))
        commands.add_groups(groups_to_add)
        commands.remove_groups(groups_to_remove)
        umapi_connector.send_commands(commands)

    def update_umapi_users_for_connector(self, umapi_info, umapi_connector):
        '''
        This is the main function that goes over adobe users and looks for and processes differences.
        It is called with a particular organization that it should manage groups against.
        It returns a map from user keys to adobe groups:
            the keys are the user keys of all the selected directory users that don't exist in the target umapi;
            the value for each key is the set of adobe groups in this umapi that the created user should be put into.
        The use of this return value by the caller is to create the user and add him to the right groups.
        :type umapi_info: UmapiTargetInfo
        :type umapi_connector: user_sync.connector.umapi.UmapiConnector
        :rtype: map(string, set)
        '''
        filtered_directory_user_by_user_key = self.filtered_directory_user_by_user_key

        # the way we construct the return vaue is to start with a map from all directory users
        # to their groups in this umapi, make a copy, and pop off any adobe users we find.
        # That way, and key/value pairs left in the map are the unmatched adobe users and their groups.
        user_to_group_map = umapi_info.get_desired_groups_by_user_key()
        user_to_group_map = {} if user_to_group_map == None else user_to_group_map.copy()

        # check to see if we should update adobe users
        options = self.options
        update_user_info = options['update_user_info']
        manage_groups = self.will_manage_groups()
        exclude_strays = self.options['exclude_strays']
        will_process_strays = self.will_process_strays

        # prepare the strays map if we are going to be processing them
        if will_process_strays:
            self.add_stray(umapi_info.get_name(), None)

        # there are certain operations we only do in the primary umapi
        in_primary_org = umapi_info.get_name() == PRIMARY_UMAPI_NAME

        # Walk all the adobe users, getting their group data, matching them with directory users,
        # and adjusting their attribute and group data accordingly.
        for umapi_user in umapi_connector.iter_users():
            # get the basic data about this user; initialize change markers to "no change"
            user_key = self.get_umapi_user_key(umapi_user)
            umapi_info.add_umapi_user(user_key, umapi_user)
            attribute_differences = {}
            current_groups = self.normalize_groups(umapi_user.get('groups'))
            groups_to_add = set()
            groups_to_remove = set()

            # If this adobe user matches any directory user, pop them out of the
            # map because we know they don't need to be created.
            # Also, keep track of the mapped groups for the directory user
            # so we can update the adobe user's groups as needed.
            desired_groups = user_to_group_map.pop(user_key, None) or set()

            # check for excluded users
            if self.is_umapi_user_excluded(in_primary_org, user_key, current_groups):
                continue

            directory_user = filtered_directory_user_by_user_key.get(user_key)
            if directory_user is None:
                # There's no selected directory user matching this adobe user
                # so we mark this adobe user as a stray, and we mark him
                # for removal from any mapped groups.
                if exclude_strays:
                    self.logger.debug("Excluding Adobe-only user: %s", user_key)
                    self.excluded_user_count += 1
                elif will_process_strays:
                    self.logger.debug("Found Adobe-only user: %s", user_key)
                    self.add_stray(umapi_info.get_name(), user_key,
                                   None if not manage_groups else current_groups & umapi_info.get_mapped_groups())
            else:
                # There is a selected directory user who matches this adobe user,
                # so mark any changed umapi attributes,
                # and mark him for addition and removal of the appropriate mapped groups
                if update_user_info or manage_groups:
                    self.logger.debug("Adobe user matched on customer side: %s", user_key)
                if update_user_info and in_primary_org:
                    attribute_differences = self.get_user_attribute_difference(directory_user, umapi_user)
                if manage_groups:
                    groups_to_add = desired_groups - current_groups
                    groups_to_remove =  (current_groups - desired_groups) & umapi_info.get_mapped_groups()

            # Finally, execute the attribute and group adjustments
            self.update_umapi_user(umapi_info, user_key, umapi_connector,
                                   attribute_differences, groups_to_add, groups_to_remove, umapi_user)

        # mark the umapi's adobe users as processed and return the remaining ones in the map
        umapi_info.set_umapi_users_loaded()
        return user_to_group_map

    def is_umapi_user_excluded(self, in_primary_org, user_key, current_groups):
        if in_primary_org:
            self.adobe_user_count += 1
            # in the primary umapi, we actually check the exclusion conditions
            identity_type, username, domain = self.parse_user_key(user_key)
            if identity_type in self.exclude_identity_types:
                self.logger.debug("Excluding adobe user (due to type): %s", user_key)
                self.excluded_user_count += 1
                return True
            if len(current_groups & self.exclude_groups) > 0:
                self.logger.debug("Excluding adobe user (due to group): %s", user_key)
                self.excluded_user_count += 1
                return True
            for re in self.exclude_users:
                if re.match(username):
                    self.logger.debug("Excluding adobe user (due to name): %s", user_key)
                    self.excluded_user_count += 1
                    return True
            self.included_user_keys.add(user_key)
            return False
        else:
            # in all other umapis, we exclude every user that
            #  doesn't match an included user from the primary umapi
            return user_key not in self.included_user_keys

    @staticmethod
    def normalize_groups(group_names):
        '''
        :type group_names: iterator(str)
        :rtype set(str)
        '''
        result = set()
        if group_names is not None:
            for group_name in group_names:
                normalized_group_name = user_sync.helper.normalize_string(group_name)
                result.add(normalized_group_name)
        return result

    def calculate_groups_to_add(self, umapi_info, user_key, desired_groups):
        '''
        Return a set of groups that have not been registered to be added.
        :type umapi_info: UmapiTargetInfo
        :type user_key: str
        :type desired_groups: set(str) 
        '''
        groups_to_add = self.get_new_groups(umapi_info.groups_added_by_user_key, user_key, desired_groups)
        if desired_groups != None and self.logger.isEnabledFor(logging.DEBUG):
            groups_already_added = desired_groups - groups_to_add
            if groups_already_added:
                self.logger.debug('Already added groups for user: %s groups: %s', user_key, groups_already_added)
        return groups_to_add

    def calculate_groups_to_remove(self, umapi_info, user_key, desired_groups):
        '''
        Return a set of groups that have not been registered to be removed.
        :type umapi_info: UmapiTargetInfo
        :type user_key: str
        :type desired_groups: set(str) 
        '''
        groups_to_remove = self.get_new_groups(umapi_info.groups_removed_by_user_key, user_key, desired_groups)
        if desired_groups is not None and self.logger.isEnabledFor(logging.DEBUG):
            groups_already_removed = desired_groups - groups_to_remove
            if len(groups_already_removed) > 0:
                self.logger.debug('Skipped removed groups for user: %s groups: %s', user_key, groups_already_removed)
        return groups_to_remove

    def get_new_groups(self, current_groups_by_user_key, user_key, desired_groups):
        '''
        Return a set of groups that have not been registered in the dictionary for the specified user.        
        :type current_groups_by_user_key: dict(str, set(str))
        :type user_key: str
        :type desired_groups: set(str) 
        '''
        new_groups = None
        if desired_groups is not None:
            current_groups = current_groups_by_user_key.get(user_key)
            if current_groups is not None:
                new_groups = desired_groups - current_groups
            else:
                new_groups = desired_groups
            if len(new_groups) > 0:
                if current_groups is None:
                    current_groups_by_user_key[user_key] = current_groups = set()
                current_groups |= new_groups
        return new_groups


    def get_user_attribute_difference(self, directory_user, umapi_user):
        differences = {}
        attributes = self.get_user_attributes(directory_user)
        for key, value in attributes.iteritems():
            umapi_value = umapi_user.get(key)
            if value != umapi_value:
                differences[key] = value
        return differences        

    def get_directory_user_key(self, directory_user):
        '''
        Identity-type aware user key management for directory users
        :type directory_user: dict
        '''
        id_type = self.get_identity_type_from_directory_user(directory_user)
        return self.get_user_key(id_type, directory_user['username'], directory_user['domain'], directory_user['email'])
    
    def get_umapi_user_key(self, umapi_user):
        '''
        Identity-type aware user key management for adobe users
        :type umapi_user: dict
        '''
        id_type = self.get_identity_type_from_umapi_user(umapi_user)
        return self.get_user_key(id_type, umapi_user['username'], umapi_user['domain'], umapi_user['email'])

    def get_user_key(self, id_type, username, domain, email=None):
        '''
        Construct the user key for a directory or adobe user.
        The user key is the stringification of the tuple (id_type, username, domain)
        but the domain part is left empty if the username is an email address.
        If the parameters are invalid, None is returned.
        :param username: (required) username of the user, can be his email
        :param domain: (optional) domain of the user
        :param email: (optional) email of the user
        :param id_type: (required) id_type of the user
        :return: string "id_type,username,domain" (or None)
        '''
        id_type = user_sync.identity_type.parse_identity_type(id_type)
        email = user_sync.helper.normalize_string(email) if email else None
        username = user_sync.helper.normalize_string(username) or email
        domain = user_sync.helper.normalize_string(domain)

        if not id_type:
            return None
        if not username:
            return None
        if username.find('@') >= 0:
            domain = ""
        elif not domain:
            return None
        return unicode(id_type) + u',' + unicode(username) + u',' + unicode(domain)

    def parse_user_key(self, user_key):
        '''Returns the identity_type, username, and domain for the user.
        The domain part is empty except if the username is not an email address.
        :rtype: tuple
        '''
        return user_key.split(',')

    def get_username_from_user_key(self, user_key):
        return self.parse_user_key(user_key)[1]

    def read_stray_key_map(self, file_path, delimiter = None):
        '''
        Load the users to be removed from a CSV file.  Returns the stray key map.
        :type file_path: str
        :type delimiter: str
        '''
        self.logger.info('Reading Adobe-only users from: %s', file_path)
        id_type_column_name = 'type'
        user_column_name = 'username'
        domain_column_name = 'domain'
        ummapi_name_column_name = 'umapi'
        rows = user_sync.helper.iter_csv_rows(file_path,
                                              delimiter = delimiter,
                                              recognized_column_names = [
                                                  id_type_column_name, user_column_name, domain_column_name,
                                                  ummapi_name_column_name,
                                              ],
                                              logger = self.logger)
        for row in rows:
            umapi_name = row.get(ummapi_name_column_name) or PRIMARY_UMAPI_NAME
            id_type = row.get(id_type_column_name)
            user = row.get(user_column_name)
            domain = row.get(domain_column_name)
            user_key = self.get_user_key(id_type, user, domain)
            if user_key:
                self.add_stray(umapi_name, None)
                self.add_stray(umapi_name, user_key)
            else:
                self.logger.error("Invalid input line, ignored: %s", row)
        user_count = len(self.get_stray_keys())
        user_plural = "" if user_count == 1 else "s"
        secondary_count = len(self.stray_key_map) - 1
        if secondary_count > 0:
            umapi_plural = "" if secondary_count == 1 else "s"
            self.logger.info('Read %d Adobe-only user%s for primary umapi, with %d secondary umapi%s',
                             user_count, user_plural, secondary_count, umapi_plural)
        else:
            self.logger.info('Read %d Adobe-only user%s.', user_count, user_plural)

    def write_stray_key_map(self):
        file_path = self.stray_list_output_path
        logger = self.logger
        logger.info('Writing Adobe-only users to: [[%s]]', file_path)
        # figure out if we should include a umapi column
        secondary_count = 0
        fieldnames = ['type', 'username', 'domain']
        for umapi_name in self.stray_key_map:
            if umapi_name != PRIMARY_UMAPI_NAME and self.get_stray_keys(umapi_name):
                if not secondary_count:
                    fieldnames.append('umapi')
                secondary_count += 1
        with open(file_path, 'wb') as output_file:
            delimiter = user_sync.helper.guess_delimiter_from_filename(file_path)            
            writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            # None sorts before strings, so sorting the keys in the map
            # puts the primary umapi first in the output, which is handy
            for umapi_name in sorted(self.stray_key_map.keys()):
                for user_key in self.get_stray_keys(umapi_name):
                    id_type, username, domain = self.parse_user_key(user_key)
                    umapi = umapi_name if umapi_name else ""
                    if secondary_count:
                        row_dict = {'type': id_type, 'username': username, 'domain': domain, 'umapi': umapi}
                    else:
                        row_dict = {'type': id_type, 'username': username, 'domain': domain}
                    writer.writerow(row_dict)
        user_count = len(self.stray_key_map.get(PRIMARY_UMAPI_NAME, []))
        user_plural = "" if user_count == 1 else "s"
        if secondary_count > 0:
            umapi_plural = "" if secondary_count == 1 else "s"
            logger.info('Wrote %d Adobe-only user%s for primary umapi, with %d secondary umapi%s',
                        user_count, user_plural, secondary_count, umapi_plural)
        else:
            logger.info('Wrote %d Adobe-only user%s.', user_count, user_plural)
            
    def log_after_mapping_hook_scope(self, before_call=None, after_call=None):
        if (before_call is None and after_call is None) or (before_call is not None and after_call is not None):
            raise ValueError("Exactly one of 'before_call', 'after_call' must be passed (and not None)")
        when = 'before' if before_call is not None else 'after'
        if before_call is not None:
            self.logger.debug('.')
            self.logger.debug('Source attrs, %s: %s', when, self.after_mapping_hook_scope['source_attributes'])
            self.logger.debug('Source groups, %s: %s', when, self.after_mapping_hook_scope['source_groups'])
        self.logger.debug('Target attrs, %s: %s', when, self.after_mapping_hook_scope['target_attributes'])
        self.logger.debug('Target groups, %s: %s', when, self.after_mapping_hook_scope['target_groups'])
        if after_call is not None:
            self.logger.debug('Hook storage, %s: %s', when, self.after_mapping_hook_scope['hook_storage'])


class UmapiConnectors(object):
    def __init__(self, primary_connector, secondary_connectors):
        '''
        :type primary_connector: user_sync.connector.umapi.UmapiConnector
        :type secondary_connectors: dict(str, user_sync.connector.umapi.UmapiConnector)
        '''
        self.primary_connector = primary_connector
        self.secondary_connectors = secondary_connectors
        
        connectors = [primary_connector]
        connectors.extend(secondary_connectors.itervalues())
        self.connectors = connectors
        
    def get_primary_connector(self):
        return self.primary_connector

    def get_secondary_connectors(self):
        return self.secondary_connectors
     
    def execute_actions(self):
        while True:
            had_work = False
            for connector in self.connectors:
                action_manager = connector.get_action_manager()
                if action_manager.has_work():
                    action_manager.flush()
                    had_work = True
            if not had_work:
                break

    
class AdobeGroup(object):

    index_map = {}

    def __init__(self, group_name, umapi_name):
        '''
        :type group_name: str
        :type umapi_name: str
        '''
        self.group_name = group_name
        self.umapi_name = umapi_name
        AdobeGroup.index_map[(group_name, umapi_name)] = self
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(frozenset(self.__dict__))
    
    def __str__(self):
        return str(self.__dict__)

    def get_qualified_name(self):
        prefix = ""
        if self.umapi_name is not None and self.umapi_name != PRIMARY_UMAPI_NAME:
            prefix = self.umapi_name + GROUP_NAME_DELIMITER
        return prefix + self.group_name

    def get_umapi_name(self):
        return self.umapi_name

    def get_group_name(self):
        return self.group_name

    @staticmethod
    def _parse(qualified_name):
        '''
        :type qualified_name: str
        :rtype: str, str
        '''
        parts = qualified_name.split(GROUP_NAME_DELIMITER)
        group_name = parts.pop()
        umapi_name = GROUP_NAME_DELIMITER.join(parts)
        if len(umapi_name) == 0:
            umapi_name = PRIMARY_UMAPI_NAME
        return group_name, umapi_name

    @classmethod
    def lookup(cls, qualified_name):
        return cls.index_map.get(cls._parse(qualified_name))

    @classmethod
    def create(cls, qualified_name):
        group_name, umapi_name = cls._parse(qualified_name)
        existing = cls.index_map.get((group_name, umapi_name))
        if existing:
            return existing
        elif len(group_name) > 0:
            return cls(group_name, umapi_name)
        else:
            return None

    @classmethod
    def iter_groups(cls):
        return cls.index_map.itervalues()


class UmapiTargetInfo(object):
    def __init__(self, name):
        '''
        :type name: str
        '''
        self.name = name
        self.mapped_groups = set()
        self.desired_groups_by_user_key = {}
        self.umapi_user_by_user_key = {}
        self.umapi_users_loaded = False
        self.stray_by_user_key = {}
        self.groups_added_by_user_key = {}
        self.groups_removed_by_user_key = {}

    def get_name(self):
        return self.name
    
    def add_mapped_group(self, group):
        '''
        :type group: str
        '''
        normalized_group_name = user_sync.helper.normalize_string(group)
        self.mapped_groups.add(normalized_group_name)

    def get_mapped_groups(self):
        return self.mapped_groups
    
    def get_desired_groups_by_user_key(self):
        return self.desired_groups_by_user_key

    def get_desired_groups(self, user_key):
        '''
        :type user_key: str
        '''
        desired_groups = self.desired_groups_by_user_key.get(user_key)
        return desired_groups     

    def add_desired_group_for(self, user_key, group):
        '''
        :type user_key: str
        :type group: str
        '''
        desired_groups = self.get_desired_groups(user_key)
        if desired_groups is None:
            self.desired_groups_by_user_key[user_key] = desired_groups = set()
        if group is not None:
            normalized_group_name = user_sync.helper.normalize_string(group)
            desired_groups.add(normalized_group_name)

    def add_umapi_user(self, user_key, user):
        '''
        :type user_key: str
        :type user: dict
        '''
        self.umapi_user_by_user_key[user_key] = user
        
    def iter_umapi_users(self):
        return self.umapi_user_by_user_key.iteritems()
    
    def get_umapi_user(self, user_key):
        '''
        :type user_key: str
        '''
        return self.umapi_user_by_user_key.get(user_key)
    
    def set_umapi_users_loaded(self):
        self.umapi_users_loaded = True
        
    def is_umapi_users_loaded(self):
        return self.umapi_users_loaded
    
    def __repr__(self):
        return "UmapiTargetInfo('name': %s)" % self.name
