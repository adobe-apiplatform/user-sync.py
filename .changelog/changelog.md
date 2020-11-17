# New Features

\#612 Various fixes and enhancements to CLI

# Bug Fixes

\#606 Adobe console connector module not found
\#607 Update UST/doc for api_key and tech_acct
\#611 Correct key data reference for decrypting
\#617 Email casing difference between UMAPI and Sign users

# Known Issues

No known issues at this time.

v2.6.1 - 2020-09-14

---

Final release of UST 2.6.0

# New Features

\#530 New directory connector: Admin Console

\#537 New Feature `--exclude-unmapped-users`

\#593 Standalone EXE Builds

\#552 Post-Sync and Sign Sync Connector

\#583 Certificate generation for adobe.io integrations (and private key encryption)

\#564 Kerberos support for LDAP connector

\#585 Disable SSL validation for UMAPI connections

\#548 Skip creation of Federated ID if Adobe ID with same email aexists

# Bug Fixes

\#578 Fix for 'invalid attribute type memberOf' at user-level LDAP request

\#584 Added whitelist for functions available inside of eval()

\#568 Python 2 build issue due to Zipp

\#561 Centos environment and dependency build issues fix

\#523 Replace / Remove unused methods

\#527 use jeepney 0.4 for py 3

\#576 Bug Fix: Email update if username (@ based) is diff from email on UMAPI

# Compatibility with Prior Versions

PEX builds have been deprecated in favor of standalone executable builds. Python is embedded in the executable, so Python is no longer required on the system to run the Sync Tool.

To upgrade to v2.6.0, simply download the Sync Tool build for your platform, extract the executable, and copy it to your User Sync Tool directory. Instead of invoking Python to run the pex (e.g. `python user-sync` or `python user-sync.pex`), just execute the tool (`./user-sync` or `.\user-sync.exe`).

# Known Issues

No known issues at this time.

# Additional Build Information

* Python 2.7 support has been removed as per \#586. All builds are currently targeted at Python 3.6.8
* This release introduces the `-noext` build variant. It disables extension configuration support.

v2.6.0 - 2020-04-30

---

UST 2.5.1

# Bug Fixes

\#578 Fix for 'invalid attribute type memberOf' at user-level LDAP request

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

No known issues at this time.

# Additional Build Information

This build is not compatible with Python 3.7

v2.5.1 - 2020-03-25

---

Final Release of UST 2.5.0

# New Features

\#475 Add support to specify LDAP authentication type in LDAP connector

\#482 Refactor CLI option handling and introduce subcommands

# Bug Fixes

\#476 `yaml.load()` is deprecated and considered unsafe.  `yaml.safe_load()` used instead

\#469 Ignore case in user exclusions

\#477, #457 Fix issue with additional group feature and `--adobe-only-user-list`

\#458 Fix invocation option override for `--adobe-only-user-action`

\#348 Make extended groups and attribute options nullable in extension config

\#471 Normalize email when comparing attributes for user updates

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

No known issues at this time.

# Additional Build Information

\#475 Switch LDAP client from python-ldap to ldap3

\#481 Resource manager

This build is not compatible with Python 3.7

v2.5.0 - 2019-06-14

---

# Release Notes for User Sync Tool Version 2.4.3

These notes apply to v2.4.3 of 2019-04-05.

# New Features

none

# Bug Fixes

none

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

Python 3.7 is not supported at this time.  See #376.

# Additional Build Information

Pinned `pycryptodome` dependency to `3.7.3` to avoid Windows path length issue.

v2.4.3 - 2019-04-05

---

# Release Notes for User Sync Tool Version 2.4.2

These notes apply to v2.4.2 of 2019-04-03.

# New Features

\#368 `--adobe-users` command line option to whitelist specific Adobe groups for sync.  Invocation option also added.

# Bug Fixes

\#438 Log a better error if directory connector not correctly configured

\#450 Fix regression introduced in 2.4

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

Python 3.7 is not supported at this time.  See #376.

# Additional Build Information

\#448 Test system overhaul

v2.4.2 - 2019-04-03

---

# Release Notes for User Sync Tool Version 2.4

These notes apply to v2.4 of 2019-01-28.


# New Features

\#398 `max_adobe_only_users` can be set to a percentage of total users.

\#323 Two-step group lookup.  Certain LDAP systems do not support group membership queries.  This feature adds new config options to `connector-ldap.yml` to enable a two-step LDAP user lookup workflow.

\#385 Support for users that have a different email-type username and email address.  Users of this type are synced by specifying both a `user_username_format` and `user_email_format` in `connector-ldap.yml`.  The username field must contain only email-type usernames.  Users with alphanumeric usernames will not be synced.  See the "Advanced Configuration" section of the User Manual for more information.

\#339 Dynamic mapping of additional groups and automatic group creation.  Introduces an optional config option to identify additional groups that a user directly belongs to.  Additional groups are matched with a list of one or more regular expressions.  These groups can be dynamically mapped to Adobe groups using regular expression substitution strings.  In addition, Adobe groups targeted by this method, as well as the standard mapping or extension config, can be automatically created by the sync tool.  New groups are created as user groups.  See the documentation for more details.

\#405 Additional enhancements and fixes to group sync
* Log "additional group" rule mapping
* Don't allow multiple source rules to map to same target group
* Catch regex substitution errors
* Remove some superfluous and confusing checks
* Secondary org support

# Bug Fixes

\#379 --user-filter and invocation default

\#381 Invocation Defaults doesn't work for "--users file"
* Not actually a bug, but `user-sync-config.yml` was updated to clarify how to specify user input file in `invocation_defaults`

\#396 LDAP error when running user-sync-v2.4rc1-win64-py2715 

# Documentation Updates

\#403 Add documentation for Azure AD / UST

\#426 Ergonomic tweaks to template configs
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

\#384 UMAPI returns truncated group list for users assigned to a large amount of groups.  This doesn't prevent the new additional group functionality from working, but it does result in unnecessary API calls to assign users to groups they already may belong to.

# Additional Build Information

User Sync is now built with umapi\_client 2.12, which supports the following new features
* Add new user groups
* Update existing user groups
* Delete user groups
* Create users with different email-type usernames and email addresses

v2.4 - 2019-01-28

---

# Release Notes for User Sync Tool Version 2.3

These notes apply to v2.3 of 2018-07-31.

## New Features

User Sync can now connect to Okta enterprise directories.  Create an Okta configuration and use the new `--connector okta` command-line argument to select that connector.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/advanced_configuration.html#the-okta-connector) for details.

There is a new command-line argument `--connector` for specifying whether to get directory information via LDAP file, by reading a CSV file, or via the Okta connector.  The default connector is `ldap`.  For CSV users, who formerly had to specify their input source with the `--users` argument, this optional argument offers the chance to specify `--users mapped` or `--users group ...` (since the CSV input can be specified with `--connector`).  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for details.

[#292](https://github.com/adobe-apiplatform/user-sync.py/issues/292) You can now specify the log file name as well as the log file directory in your configuration file.  The name is specified by giving a Python format string which, when applied to a Python `datetime` value at the start of the run, produces the name of the log file.  The default value of this string is backwards-compatible with prior User Sync behavior.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/configuring_user_sync_tool.html#configure-logging) for details.

[#299](https://github.com/adobe-apiplatform/user-sync.py/issues/299) You can now use an `invocation_defaults` section to specify desired values for command-line arguments in the main configuration file.  This can make it a lot easier to repeat runs with a stable set of arguments, even when running interactively rather than from a script.  The sample main configuration file specifies the configuration parameters to use as well as the syntax for specifying values.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for full details.

[#322](https://github.com/adobe-apiplatform/user-sync.py/issues/322), [#319](https://github.com/adobe-apiplatform/user-sync.py/issues/319) As it has been with email, you can now use formatted combinations of ldap/okta attributes for the Adobe-side first name, last name, and country.  (See the sample configuration files for details.)  You can also specify the country code in lower case.

## Bug Fixes

[#305](https://github.com/adobe-apiplatform/user-sync.py/issues/305) General issues with Okta connector.

[#306](https://github.com/adobe-apiplatform/user-sync.py/issues/306) v2.2.2 crashes if country code not specified.

[#308](https://github.com/adobe-apiplatform/user-sync.py/issues/308) docs are unclear about how to set PEX_ROOT.

[#314](https://github.com/adobe-apiplatform/user-sync.py/issues/314) invocation_defaults section should be optional.

[#315](https://github.com/adobe-apiplatform/user-sync.py/issues/315) Can't specify --user-filter or other string-valued args.

[#318](https://github.com/adobe-apiplatform/user-sync.py/issues/318) Fix the README build instructions regarding dbus.

[#324](https://github.com/adobe-apiplatform/user-sync.py/issues/324) Handle LDAP servers with no support for PagedResults.

[#325](https://github.com/adobe-apiplatform/user-sync.py/issues/325) Adding '--process-groups' doesn't override the default.

[#364](https://github.com/adobe-apiplatform/user-sync.py/issues/364) Okta decode error

[#365](https://github.com/adobe-apiplatform/user-sync.py/issues/365) Using adobe-only-user-list does not work

## Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.  The `--users file` argument is still accepted, and is equivalent to (although more limited than) specifying `--connector csv`.

## Known Issues

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available for that platform (from the OS vendor, if they provide one, from [python.org](http://python.org) otherwise).  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

## Additional Build Information

User Sync is now built with PyLDAP 2.4.45.

User Sync is now built with umapi_client 2.10.  This allows mocking the UMAPI connection for use with a test framework.  See the test_framework directory in the source tree for more details.

v2.3 - 2018-08-01
