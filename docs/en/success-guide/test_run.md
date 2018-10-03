---
layout: default
lang: en
nav_link: Test Run
nav_level: 2
nav_order: 290
---

# Make a Test Run To Check Configuration

[Previous Section](setup_config_files.md) \| [Back to Contents](index.md) \| [Next Section](monitoring.md)

To invoke user sync:

Windows:      **python user-sync.pex ….**

Unix, OSX:     **./user-sync ….**


Give it a try:

	./user-sync –v            Report version
	./user-sync –h            Help on command line args

&#9744; Try the 2 commands above and verify that they are working. (On Windows, the command is slightly different.)


![img](images/test_run_screen.png)

&#9744; Next, try a sync limited to mapped group and run in test mode.

	./user-sync -t --users mapped --process-groups --adobe-only-user-action exclude

The command above will sync only the user(s) in the mapped group specified in user-sync-config.yml. If the users does not exist in the Admin Console, it should result in an attempt to create the user(s) and add them to any groups that are mapped from their directory groups.  Because of running in test mode (-t), the run of user-sync will only attempt to create the user and not actually do it.  The `--adobe-only-user-action exclude` option will prevent updates to any user accounts that already exist in the Adobe organization.

&#9744; Next, try a sync without test mode.  This should actually create the user and add to groups.

	./user-sync --users mapped --process-groups --adobe-only-user-action exclude

&#9744; Next, go check on the Adobe Admin Console if the user has appeared and the group memberships have been added.

&#9744; Next, rerun the same command.  User sync should not attempt to recreate and re-add the user to groups.  It should detect that the user already exists and is a member of the user group or PC and do nothing.

If these are all working as expected, you are ready to make a live run.  If you don't have too many users in your directory group, you can try it now.  If you have more than a few hundred, it could take a long time so don't do the execution until you are ready to have a command running for many hours.  Also, go over the next few section before doing this in case there are other relevant command line options.




[Previous Section](setup_config_files.md) \| [Back to Contents](index.md) \| [Next Section](monitoring.md)

