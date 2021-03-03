# Release Notes for User Sync Tool Version 2.4

These notes apply to v2.4 of 2018-01-28.

# New Features

[#398](https://github.com/adobe-apiplatform/user-sync.py/issues/398) `max_adobe_only_users` can be set to a percentage of total users.

[#323](https://github.com/adobe-apiplatform/user-sync.py/issues/323) Two-step group lookup.  Certain LDAP systems do not support group membership queries.  This feature adds new config options to `connector-ldap.yml` to enable a two-step LDAP user lookup workflow.

[#385](https://github.com/adobe-apiplatform/user-sync.py/issues/385) Support for users that have a different email-type username and email address.  Users of this type are synced by specifying both a `user_username_format` and `user_email_format` in `connector-ldap.yml`.  The username field must contain only email-type usernames.  Users with alphanumeric usernames will not be synced.  See the "Advanced Configuration" section of the User Manual for more information.

[#339](https://github.com/adobe-apiplatform/user-sync.py/issues/339) Dynamic mapping of additional groups and automatic group creation.  Introduces an optional config option to identify additional groups that a user directly belongs to.  Additional groups are matched with a list of one or more regular expressions.  These groups can be dynamically mapped to Adobe groups using regular expression substitution strings.  In addition, Adobe groups targeted by this method, as well as the standard mapping or extension config, can be automatically created by the sync tool.  New groups are created as user groups.  See the documentation for more details.

[#405](https://github.com/adobe-apiplatform/user-sync.py/pull/405) Additional enhancements and fixes to group sync
* Log "additional group" rule mapping
* Don't allow multiple source rules to map to same target group
* Catch regex substitution errors
* Remove some superfluous and confusing checks
* Secondary org support

# Bug Fixes

[#379](https://github.com/adobe-apiplatform/user-sync.py/issues/379) --user-filter and invocation default

[#381](https://github.com/adobe-apiplatform/user-sync.py/issues/381) Invocation Defaults doesn't work for "--users file"
* Not actually a bug, but `user-sync-config.yml` was updated to clarify how to specify user input file in `invocation_defaults`

[#396](https://github.com/adobe-apiplatform/user-sync.py/issues/396) LDAP error when running user-sync-v2.4rc1-win64-py2715

# Documentation Updates

[#403](https://github.com/adobe-apiplatform/user-sync.py/issues/403) Add documentation for Azure AD / UST

[#426](https://github.com/adobe-apiplatform/user-sync.py/pull/426) Ergonomic tweaks to template configs
* Removed Number from the sample template
* Connector-umapi.yml
  - set private key path to just private.key
* Connector-ldap.yml
  - set page size to 1000 (Active Directory Default)
  - user\_username\_format example to just {sAMAccountName}
* User-Sync-Config.yml
  - Default to FederatedID
  - Tweaked the example to match with current use case
  - Enable Logging by Default
  - Default Invocation - Set to Process-group and Users Mapped to avoid accidentally directory dump to Admin console.

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

Python 3.7 is not supported at this time.  See #376.

[#384](https://github.com/adobe-apiplatform/user-sync.py/issues/384) UMAPI returns truncated group list for users assigned to a large amount of groups.  This doesn't prevent the new additional group functionality from working, but it does result in unnecessary API calls to assign users to groups they already may belong to.

# Additional Build Information

User Sync is now built with umapi\_client 2.12, which supports the following new features
* Add new user groups
* Update existing user groups
* Delete user groups
* Create users with different email-type usernames and email addresses
