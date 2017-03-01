# Release Notes for User Sync Tool Version 1.1 
**2017-03-03.**

## Updating from prior versions

This version has 2 new required configuration items.  If you are using an earlier version, you will need to add the following entires to your main user-sync-config.yaml file:

    limits:
        max_deletions_per_run: 10    # if --remove-nonexistent-users is specified, this is the most users that will be removed.  Others will be left for a later run.  A critical message will be logged.
        max_missing_users: 200       # if more than this number of user accounts are not found in the directory, user sync will abort with an error and a critical message will be logged.

To update your installation, download the release for your platform and replace the user-sync or user-sync.pex file with the new one.  Same the old one in case of problems

Because this version contains a more aggressive --process-groups function (a bug fix) you may want to run with --test-only first and make sure nothing unexpected is happening.

## New Features / Bugs Fixed

1. Ability to specify additional directory attributes to load and specify a code snippet to implement complex mappings from directory information to Adobe user information and group membership.  This is covered in more detail in the updated documentation.

2. Releases for different platforms are packaged separately so you only have to download the platform(s) you want.  You do have to download the example configuration files and documentation separately.

3. User removal limits and guards.  There are some new features to prevent user sync from accidentally removing large numbers of users in the event of misconfiguration or changes in the directory which result in users not being returned from queries.

4. A bug preventing sync from working properly with Federated domains with username rather than email based logins is fixed.

5. A bug in --process-groups was fixed.  Details below.

## Changes in Behavior

A bug in --process-groups was fixed.  Previously, users present in the Adobe admin console but not in the directory were not removed from groups that were mapped in the user sync configuration file.  This is now fixed.  A group (user group or product configuration) that is mapped from a directory group is assumed to be under user sync control and any users in such groups that are not in the directory and in groups in the directory mapped to those Adobe groups are removed.

This release of user sync should be compatible and have no other behavior changes.

## Compatibility with Prior Versions

Other than as noted above, existing configuration files and should work and have the same behavior.
