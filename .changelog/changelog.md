| tag | date | title |
|---|---|---|
| v2.7.6 | 2023-01-12 | User Sync Tool v2.7.6 |

# Features

* 4c4545a Extend "additional groups" awareness/support to all directory connectors

# Fixes

* 183e1d2 Fix bug when writing Adobe-only users to file (#801)
* 79ce27d Non-zero exit code for certain error conditions (#803)
* 651d211 Deal with emails, not usernames in CSV adobe-only features (write to CSV, read from CSV) (#808)

# Documentation

* c54a9eb Update Additional Groups documentation to discuss all directory connector types

---

| tag | date | title |
|---|---|---|
| v2.7.5 | 2022-09-29 | User Sync Tool v2.7.5 |

# Bug Fixes
* fbeb468b Update Sign API model to ignore unknown attributes
* 637a2bf7 Get Okta token from config securely

# Documentation Updates
* Documentation is now built from branch `user-guide`
* eab9825 Create GHA workflow to build docs

---

| tag | date | title |
|---|---|---|
| v2.7.4 | 2022-09-07 | User Sync Tool v2.7.4 |

# Bug Fixes
* 4513fcf6, b8be71f8 Updates to Sign API model
* f5ae3573 Better Okta error handling
* #798 Fix timing of Sign API connection
* #794 Create users with email-type usernames in single command step (instead of two-step workflow)

# Documentation Updates
* 20ebaebd Document alternate /tmp solution
* 27a99b44, 113a418b Add page for certificate update

# Misc Changes
* #785 Deprecation warning error type
* #791 Remove CLI args from Windows batch files

---

| tag | date | title |
|---|---|---|
| v2.7.3 | 2022-03-29 | User Sync Tool v2.7.3 |

\#755 Fix Sign email comparison issue
\#774 ESM trustee sync fix
\#761 Remove six dependency
\#776 Sign timeout error fix
fe073bf7 Update Sign summary log counts

---

| tag | date | title |
|---|---|---|
| v2.7.2 | 2022-03-21 | User Sync Tool v2.7.2 |

\#763 Fix CentOS build
\#759 Resolve Windows keyring error

---

| tag | date | title |
|---|---|---|
| v2.7.1 | 2022-03-14 | User Sync Tool v2.7.1 |

* \#773 Sync signal logic tweaks

---

| tag | date | title |
|---|---|---|
| v2.7.0 | 2021-12-02 | User Sync Tool v2.7.0 |

# New Features

**Revamped Sign Sync**

Sign Sync has been overhauled. It is now implemented as a separate workflow with an alternate entrypoint command (`sign-sync`).

Feature summary

- Primary config for Sign Sync is `sign-sync-config.yml`
- Sign connector config - `connector-sign.yml`
- All identity sources are supported
- Sync supports multiple Sign targets
- Full user lifecycle management for standalone Sign environments
- Mapping structure to manage Sign group assignments and admin privileges
- Same logging options as UMAPI sync
- Sign API data is cached
- Tool to migrate post-sync config

Architecture changes

- New `engine` module
- `rules.py` refactored to `engine.umapi`
- `config.py` refctored to multi-file module
- Sign API client is top-level (parallel to `user_sync` module)
- `post_sync` has been removed

Notes:

- User multi-group (UMG) is not supported at this time
- The Sign client uses Sign API v6

Documentation here - https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/sign_sync.html

**Enhanced ESM Support**

Fixed an issue when syncing to trustee consoles that use Enterprise Storage Model (ESM).
New config option `uses_business_id` in UMAPI connector config ensures that users are
handled correctly.

See https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/advanced_configuration.html#esm-secondary-targets

---

| tag | date | title |
|---|---|---|
| v2.7.0rc4 | 2021-11-18 | User Sync Tool v2.7.0rc4 |

# New Features

**Revamped Sign Sync**

Sign Sync has been overhauled. It is now implemented as a separate workflow with an alternate entrypoint command (`sign-sync`).

Feature summary

- Primary config for Sign Sync is `sign-sync-config.yml`
- Sign connector config - `connector-sign.yml`
- All identity sources are supported
- Sync supports multiple Sign targets
- Full user lifecycle management for standalone Sign environments
- Mapping structure to manage Sign group assignments and admin privileges
- Same logging options as UMAPI sync
- Sign API data is cached
- Tool to migrate post-sync config

Architecture changes

- New `engine` module
- `rules.py` refactored to `engine.umapi`
- `config.py` refctored to multi-file module
- Sign API client is top-level (parallel to `user_sync` module)
- `post_sync` has been removed

Notes:

- User multi-group (UMG) is not supported at this time
- The Sign client uses Sign API v6

Documentation here - https://github.com/adobe-apiplatform/user-sync.py/blob/v2-sign-phase-2/docs/en/user-manual/sign_sync.md

---

| tag | date | title |
|---|---|---|
| v2.7.0rc3 | 2021-11-08 | User Sync Tool v2.7.0rc3 |

# New Features

**Revamped Sign Sync**

Sign Sync has been overhauled. It is now implemented as a separate workflow with an alternate entrypoint command (`sign-sync`).

Feature summary

- Primary config for Sign Sync is `sign-sync-config.yml`
- Sign connector config - `connector-sign.yml`
- All identity sources are supported
- Sync supports multiple Sign targets
- Full user lifecycle management for standalone Sign environments
- Mapping structure to manage Sign group assignments and admin privileges
- Same logging options as UMAPI sync
- Sign API data is cached

Architecture changes

- New `engine` module
- `rules.py` refactored to `engine.umapi`
- `config.py` refctored to multi-file module
- Sign API client is top-level (parallel to `user_sync` module)
- `post_sync` has been removed

Notes:

- User multi-group (UMG) is not supported at this time
- The Sign client uses Sign API v6

Documentation here - https://github.com/adobe-apiplatform/user-sync.py/blob/v2-sign-phase-2/docs/en/user-manual/sign_sync.md

---

| tag | date | title |
|---|---|---|
| v2.7.0rc2 | 2021-10-22 | User Sync Tool v2.7.0rc2 |

# New Features

**Revamped Sign Sync**

Sign Sync has been overhauled. It is now implemented as a separate workflow with an alternate entrypoint command (`sign-sync`).

Feature summary

- Primary config for Sign Sync is `sign-sync-config.yml`
- Sign connector config - `connector-sign.yml`
- All identity sources are supported
- Sync supports multiple Sign targets
- Full user lifecycle management for standalone Sign environments
- Mapping structure to manage Sign group assignments and admin privileges
- Same logging options as UMAPI sync

Architecture changes

- New `engine` module
- `rules.py` refactored to `engine.umapi`
- `config.py` refctored to multi-file module
- Sign API client is top-level (parallel to `user_sync` module)
- `post_sync` has been removed

Notes:

- User multi-group (UMG) is not supported at this time
- The Sign client uses Sign API v5

Documentation here - https://github.com/adobe-apiplatform/user-sync.py/blob/v2-sign-phase-2/docs/en/user-manual/sign_sync.md

---

| tag | date | title |
|---|---|---|
| v2.7.0rc1 | 2021-10-07 | User Sync Tool v2.7.0rc1 |

# New Features

**Revamped Sign Sync**

Sign Sync has been overhauled. It is now implemented as a separate workflow with an alternate entrypoint command (`sign-sync`).

Feature summary

- Primary config for Sign Sync is `sign-sync-config.yml`
- Sign connector config - `connector-sign.yml`
- All identity sources are supported
- Sync supports multiple Sign targets
- Full user lifecycle management for standalone Sign environments
- Mapping structure to manage Sign group assignments and admin privileges
- Same logging options as UMAPI sync

Architecture changes

- New `engine` module
- `rules.py` refactored to `engine.umapi`
- `config.py` refctored to multi-file module
- Sign API client is top-level (parallel to `user_sync` module)
- `post_sync` has been removed

Notes:

- User multi-group (UMG) is not supported at this time
- The Sign client uses Sign API v5

Documentation is forthcoming.

---

| tag | date | title |
|---|---|---|
| v2.6.6 | 2021-11-04 | User Sync Tool v2.6.6 |

# Bug Fixes

\#745 - Management actions halted when max Adobe-only limit exceeded

---

| tag | date | title |
|---|---|---|
| v2.6.5 | 2021-09-16 | User Sync Tool v2.6.5 |

\#728 - Fix keyring misidentification issue
\#731 - None-type issue with user commands
\#732 - Executable fails on Ubuntu 18.04 (bionic)

# Build Information

* Builds are now made with Python 3.9 on all platforms
* Separate build for Ubuntu Bionic (18.04)

---

| tag | date | title |
|---|---|---|
| v2.6.4 | 2021-08-31 | User Sync Tool v2.6.4 |

# Bug Fixes

\#723 - Start/end sync signals
\#700 - Fix some issues with SSL verification
\#623 - Fix Adobe-only list with post-sync

# Misc

\#591 - Document Two-Step Lookup
\#676 - Introduce Changelog

---

| tag | date | title |
|---|---|---|
| v2.6.3 | 2021-07-15 | User Sync Tool v2.6.3 |

# Bug Fixes

\#700 - Fix some issues with SSL verification
\#623 - Fix Adobe-only list with post-sync

# Misc

\#591 - Document Two-Step Lookup
\#676 - Introduce Changelog

---

| tag | date | title |
|---|---|---|
| v2.6.2 | 2020-12-04 | User Sync Tool v2.6.2 |

v2.6.2 - 2020-12-04

# New Features

\#598 - Add logging for user actions and umapi progress
\#596 - Add info about platform and test mode

# Bug Fixes

\#659 - Support Specifying Domain Name for Kerberos Authentication
\#663 - Prevent start_tls before Bind on LDAPS Connection

---

| tag | date | title |
|---|---|---|
| v2.6.1 | 2020-09-16 | User Sync Tool v2.6.1 |

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

| tag | date | title |
|---|---|---|
| v2.6.0 | 2020-04-30 | User Sync Tool v2.6.0 |

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

| tag | date | title |
|---|---|---|
| v2.6.0rc3 | 2020-04-15 | User Sync Tool v2.6.0rc3 |

Third Release Candidate of UST 2.6.0

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/latest).

# New Features

\#530 New directory connector: Admin Console

\#537 New Feature `--exclude-unmapped-users`

\#593 Standalone EXE Builds

\#552 Post-Sync and Sign Sync Connector

# Bug Fixes

\#578 Fix for 'invalid attribute type memberOf' at user-level LDAP request

\#584 Added whitelist for functions available inside of eval()

\#568 Python 2 build issue due to Zipp

\#561 Centos environment and dependency build issues fix

\#523 Replace / Remove unused methods

\#527 use jeepney 0.4 for py 3

# Compatibility with Prior Versions

PEX builds have been deprecated in favor of standalone executable builds. Python is embedded in the executable, so Python is no longer required on the system to run the Sync Tool.

To upgrade to v2.6.0, simply download the Sync Tool build for your platform, extract the executable, and copy it to your User Sync Tool directory. Instead of invoking Python to run the pex (e.g. `python user-sync` or `python user-sync.pex`), just execute the tool (`./user-sync` or `.\user-sync.exe`).

# Known Issues

No known issues at this time.

# Additional Build Information

* Python 2.7 support has been removed as per \#586. All builds are currently targeted at Python 3.6.8
* This release introduces the `-noext` build variant. It disables extension configuration support.

---

| tag | date | title |
|---|---|---|
| v2.5.1 | 2020-03-25 | User Sync Tool v2.5.1 |

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

| tag | date | title |
|---|---|---|
| v2.6.0rc2 | 2020-03-24 | User Sync Tool v2.6.0rc2 |

Second Release Candidate of UST 2.6.0

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.5.0).

# New Features

\#530 New directory connector: Admin Console

\#537 New Feature `--exclude-unmapped-users`

# Bug Fixes

\#578 Fix for 'invalid attribute type memberOf' at user-level LDAP request

\#584 Added whitelist for functions available inside of eval()

\#568 Python 2 build issue due to Zipp

\#561 Centos environment and dependency build issues fix

\#523 Replace / Remove unused methods

\#527 use jeepney 0.4 for py 3

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

No known issues at this time.

# Additional Build Information

This build is not compatible with Python 3.7

---

| tag | date | title |
|---|---|---|
| v2.6.0rc1 | 2019-08-26 | User Sync Tool v2.6.0rc1 |

First Release Candidate of UST 2.6.0

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.5.0).

# New Features

\#530 New directory connector: Admin Console

# Bug Fixes

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

No known issues at this time.

# Additional Build Information

This build is not compatible with Python 3.7

---

| tag | date | title |
|---|---|---|
| v2.5 | 2019-06-14 | User Sync Tool v2.5.0 |

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

| tag | date | title |
|---|---|---|
| v2.5.0rc3 | 2019-05-30 | User Sync Tool v2.5.0rc3 |

Third Release Candidate of UST 2.5.0

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.4.3).

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

---

| tag | date | title |
|---|---|---|
| v2.5.0rc2 | 2019-05-04 | User Sync Tool v2.5.0rc2 |

Second Release Candidate of UST 2.5.0

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.4.3).

# New Features

\#475 Add support to specify LDAP authentication type in LDAP connector

\#482 Refactor CLI option handling and introduce subcommands

# Bug Fixes

\#476 `yaml.load()` is deprecated and considered unsafe.  `yaml.safe_load()` used instead

\#469 Ignore case in user exclusions

\#477, #457 Fix issue with additional group feature and `--adobe-only-user-list`

\#458 Fix invocation option override for `--adobe-only-user-action`

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

No known issues at this time.

# Additional Build Information

\#475 Switch LDAP client from python-ldap to ldap3

\#481 Resource manager

This build is not compatible with Python 3.7

---

| tag | date | title |
|---|---|---|
| v2.5.0rc1 | 2019-04-10 | User Sync Tool v2.5.0rc1 |

First Release Candidate of UST 2.5.0

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.4.3).

# New Features

\#475 Add support to specify LDAP authentication type in LDAP connector

# Bug Fixes

\#476 `yaml.load()` is deprecated and considered unsafe.  `yaml.safe_load()` used instead

\#469 Ignore case in user exclusions

\#477, #457 Fix issue with additional group feature and `--adobe-only-user-list`

\#458 Fix invocation option override for `--adobe-only-user-action`

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issuess

No known issues at this time.

# Additional Build Information

\#475 Switch LDAP client from python-ldap to ldap3

This build is not compatible with Python 3.7

---

| tag | date | title |
|---|---|---|
| v2.4.3 | 2019-04-05 | User Sync Tool v2.4.3 |

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

| tag | date | title |
|---|---|---|
| v2.4.2 | 2019-04-03 | User Sync Tool v2.4.2 |

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

| tag | date | title |
|---|---|---|
| v2.4 | 2019-01-28 | User Sync Tool v2.4 |

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

| tag | date | title |
|---|---|---|
| v2.4rc3 | 2019-01-14 | User Sync Tool v2.4rc3 |

Third Release Candidate of UST 2.4

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.3).

# New Features

#385 Support for users that have a different email-type username and email address.  Users of this type are synced by specifying both a `user_username_format` and `user_email_format` in `connector-ldap.yml`.  The username field must contain only email-type usernames.  Users with alphanumeric usernames will not be synced.  See the "Advanced Configuration" section of the User Manual for more information.

#339 Dynamic mapping of additional groups and automatic group creation.  Introduces an optional config option to identify additional groups that a user directly belongs to.  Additional groups are matched with a list of one or more regular expressions.  These groups can be dynamically mapped to Adobe groups using regular expression substitution strings.  In addition, Adobe groups targeted by this method, as well as the standard mapping or extension config, can be automatically created by the sync tool.  New groups are created as user groups.  See the documentation for more details.

#405 Additional enhancements and fixes to group sync
* Log "additional group" rule mapping
* Don't allow multiple source rules to map to same target group
* Catch regex substitution errors
* Remove some superfluous and confusing checks
* Secondary org support

# Bug Fixes

#379 --user-filter and invocation default

#381 Invocation Defaults doesn't work for "--users file"
* Not actually a bug, but `1 user-sync-config.yml` was updated to clarify how to specify user input file in `invocation_defaults`

#396 LDAP error when running user-sync-v2.4rc1-win64-py2715 

# Documentation Updates

#403 Add documentation for Azure AD / UST

#426 Ergonomic tweaks to template configs
* Removed Number from the sample template
* Connector-umapi.yml
  - set private key path to just private.key
* Connector-ldap.yml
  - set page size to 1000 (Active Directory Default)
  - user_username_format example to just {sAMAccountName}
* User-Sync-Config.yml
  - Default to FederatedID
  - Tweaked the example to match with current use case
  - Enable Logging by Default
  - Default Invocation - Set to Process-group and Users Mapped to avoid accidentally directory dump to Admin console.

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

Python 3.7 is not supported at this time.  See #376.

#384 UMAPI returns truncated group list for users assigned to a large amount of groups.  This doesn't prevent the new additional group functionality from working, but it does result in unnecessary API calls to assign users to groups they already may belong to.

# Additional Build Information

User Sync is now built with umapi_client 2.12, which supports the following new features
* Add new user groups
* Update existing user groups
* Delete user groups
* Create users with different email-type usernames and email addresses

---

| tag | date | title |
|---|---|---|
| v2.4rc2 | 2018-11-30 | User Sync Tool v2.4rc2 |

Second Release Candidate of UST 2.4

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.3).

# New Features

#339 Dynamic mapping of additional groups and automatic group creation.  Introduces an optional config option to identify additional groups that a user directly belongs to.  Additional groups are matched with a list of one or more regular expressions.  These groups can be dynamically mapped to Adobe groups using regular expression substitution strings.  In addition, Adobe groups targeted by this method, as well as the standard mapping or extension config, can be automatically created by the sync tool.  New groups are created as user groups.  See the documentation for more details.

#405 Additional enhancements and fixes to group sync
* Log "additional group" rule mapping
* Don't allow multiple source rules to map to same target group
* Catch regex substitution errors
* Remove some superfluous and confusing checks
* Secondary org support

# Bug Fixes

#379 --user-filter and invocation default

#381 Invocation Defaults doesn't work for "--users file"
* Not actually a bug, but `1 user-sync-config.yml` was updated to clarify how to specify user input file in `invocation_defaults`

#396 LDAP error when running user-sync-v2.4rc1-win64-py2715 

# Documentation Updates

#403 Add documentation for Azure AD / UST

#426 Ergonomic tweaks to template configs
* Removed Number from the sample template
* Connector-umapi.yml
  - set private key path to just private.key
* Connector-ldap.yml
  - set page size to 1000 (Active Directory Default)
  - user_username_format example to just {sAMAccountName}
* User-Sync-Config.yml
  - Default to FederatedID
  - Tweaked the example to match with current use case
  - Enable Logging by Default
  - Default Invocation - Set to Process-group and Users Mapped to avoid accidentally directory dump to Admin console.

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

Python 3.7 is not supported at this time.  See #376.

#384 UMAPI returns truncated group list for users assigned to a large amount of groups.  This doesn't prevent the new additional group functionality from working, but it does result in unnecessary API calls to assign users to groups they already may belong to.

# Additional Build Information

User Sync is now built with umapi_client 2.11, which can add, update, and delete user groups.

---

| tag | date | title |
|---|---|---|
| v2.4rc1 | 2018-08-31 | User Sync Tool v2.4rc1 |

First Release Candidate of UST 2.4

# Unstable Warning

This is an unstable pre-release intended for testing and feature integration.  If you don't need any of the new features or bug fixes listed here, please use the [latest stable release](https://github.com/adobe-apiplatform/user-sync.py/releases/tag/v2.3).

# New Features

#339 Dynamic mapping of additional groups and automatic group creation.  Introduces an optional config option to identify additional groups that a user directly belongs to.  Additional groups are matched with a list of one or more regular expressions.  These groups can be dynamically mapped to Adobe groups using regular expression substitution strings.  In addition, Adobe groups targeted by this method, as well as the standard mapping or extension config, can be automatically created by the sync tool.  New groups are created as user groups.  See the documentation for more details.

# Bug Fixes

#379 --user-filter and invocation default

#381 Invocation Defaults doesn't work for "--users file"
* Not actually a bug, but `1 user-sync-config.yml` was updated to clarify how to specify user input file in `invocation_defaults`

# Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.

# Known Issues

Python 3.7 is not supported at this time.

#384 UMAPI returns truncated group list for users assigned to a large amount of groups.  This doesn't prevent the new additional group functionality from working, but it does result in unnecessary API calls to assign users to groups they already may belong to.

# Additional Build Information

User Sync is now built with umapi_client 2.11, which can add, update, and delete user groups.

---

| tag | date | title |
|---|---|---|
| v2.3 | 2018-08-01 | User Sync Tool v2.3 |

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

---

| tag | date | title |
|---|---|---|
| v2.3rc4 | 2018-01-28 | Fourth release candidate for v2.3 |

These notes apply to v2.3rc4 of 2018-01-29.

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

## Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.  The `--users file` argument is still accepted, and is equivalent to (although more limited than) specifying `--connector csv`.

## Known Issues

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available for that platform (from the OS vendor, if they provide one, from [python.org](http://python.org) otherwise).  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

## Additional Build Information

User Sync is now built with PyLDAP 2.4.45.

User Sync is now built with umapi_client 2.10.  This allows mocking the UMAPI connection for use with a test framework.  See the test_framework directory in the source tree for more details.

---

| tag | date | title |
|---|---|---|
| v2.3rc3 | 2017-12-10 | Third release candidate for v2.3 |

These notes apply to v2.3rc3 of 2017-12-10.

## New Features

User Sync can now connect to Okta enterprise directories.  Create an Okta configuration and use the new `--connector okta` command-line argument to select that connector.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/advanced_configuration.html#the-okta-connector) for details.

There is a new command-line argument `--connector` for specifying whether to get directory information via LDAP file, by reading a CSV file, or via the Okta connector.  The default connector is `ldap`.  For CSV users, who formerly had to specify their input source with the `--users` argument, this optional argument offers the chance to specify `--users mapped` or `--users group ...` (since the CSV input can be specified with `--connector`).  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for details.

[#292](https://github.com/adobe-apiplatform/user-sync.py/issues/292) You can now specify the log file name as well as the log file directory in your configuration file.  The name is specified by giving a Python format string which, when applied to a Python `datetime` value at the start of the run, produces the name of the log file.  The default value of this string is backwards-compatible with prior User Sync behavior.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/configuring_user_sync_tool.html#configure-logging) for details.

[#299](https://github.com/adobe-apiplatform/user-sync.py/issues/299) You can now use an `invocation_defaults` section to specify desired values for command-line arguments in the main configuration file.  This can make it a lot easier to repeat runs with a stable set of arguments, even when running interactively rather than from a script.  The sample main configuration file specifies the configuration parameters to use as well as the syntax for specifying values.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for full details.

## Bug Fixes

[#305](https://github.com/adobe-apiplatform/user-sync.py/issues/305) General issues with Okta connector.

[#306](https://github.com/adobe-apiplatform/user-sync.py/issues/306) v2.2.2 crashes if country code not specified.

[#314](https://github.com/adobe-apiplatform/user-sync.py/issues/314) invocation_defaults section should be optional.

[#315](https://github.com/adobe-apiplatform/user-sync.py/issues/315) Can't specify --user-filter or other string-valued args.

## Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.  The `--users file` argument is still accepted, and is equivalent to (although more limited than) specifying `--connector csv`.

## Known Issues

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available for that platform (from the OS vendor, if they provide one, from [python.org](http://python.org) otherwise).  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

## Additional Build Information

User Sync is now built with PyLDAP 2.4.45.

User Sync is now built with umapi_client 2.10.  This allows mocking the UMAPI connection for use with a test framework.  See the `test_framework` directory in the source tree for more details.

---

| tag | date | title |
|---|---|---|
| v2.3rc2 | 2017-12-04 | Second release candidate for v2.3 |

These notes apply to v2.3rc2 of 2017-12-03.

## New Features

User Sync can now connect to Okta enterprise directories.  Create an Okta configuration and use the new `--connector okta` command-line argument to select that connector.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/advanced_configuration.html#the-okta-connector) for details.

There is a new command-line argument `--connector` for specifying whether to get directory information via LDAP file, by reading a CSV file, or via the Okta connector.  The default connector is `ldap`.  For CSV users, who formerly had to specify their input source with the `--users` argument, this optional argument offers the chance to specify `--users mapped` or `--users group ...` (since the CSV input can be specified with `--connector`).  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for details.

[#292](https://github.com/adobe-apiplatform/user-sync.py/issues/292) You can now specify the log file name as well as the log file directory in your configuration file.  The name is specified by giving a Python format string which, when applied to a Python `datetime` value at the start of the run, produces the name of the log file.  The default value of this string is backwards-compatible with prior User Sync behavior.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/configuring_user_sync_tool.html#configure-logging) for details.

[#299](https://github.com/adobe-apiplatform/user-sync.py/issues/299) You can now use an `invocation_defaults` section to specify desired values for command-line arguments in the main configuration file.  This can make it a lot easier to repeat runs with a stable set of arguments, even when running interactively rather than from a script.  The sample main configuration file specifies the configuration parameters to use as well as the syntax for specifying values.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for full details.

## Bug Fixes

[#305](https://github.com/adobe-apiplatform/user-sync.py/issues/305) General issues with Okta connector.

[#306](https://github.com/adobe-apiplatform/user-sync.py/issues/306) v2.2.2 crashes if country code not specified.

## Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.  The `--users file` argument is still accepted, and is equivalent to (although more limited than) specifying `--connector csv`.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release (see the setup.py file for the specific version).  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available for that platform (from the OS vendor, if they provide one, from [python.org](http://python.org) otherwise).  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

---

| tag | date | title |
|---|---|---|
| v2.3rc1 | 2017-11-20 | okta connector: v2.3rc1 |

These notes apply to v2.3rc1 of 2017-11-20.  (There are still bugs and enhancements slated for v2.3, so there will be at least one more release candidate.)

## New Features

User Sync can now connect to Okta enterprise directories.  Create an Okta configuration and use the new `--connector okta` command-line argument to select that connector.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/advanced_configuration.html#the-okta-connector) for details.

There is a new command-line argument `--connector` for specifying whether to get directory information via LDAP, by reading a CSV file, or via the Okta connector.  The default connector is `ldap`.  For CSV users, who formerly had to specify their input source with the `--users` argument, this optional argument offers the chance to specify `--users mapped` or `--users group ...` (since the CSV input can be specified with `--connector`).  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for details.

## Bug Fixes

[#305](https://github.com/adobe-apiplatform/user-sync.py/issues/305) General issues with Okta connector.

[#306](https://github.com/adobe-apiplatform/user-sync.py/issues/306) v2.2.2 crashes if country code not specified.

## Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.  The `--users file` argument is still accepted, and is equivalent to (although more limited than) specifying `--connector csv`.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release (see the setup.py file for the specific version).  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available for that platform (from the OS vendor, if they provide one, from [python.org](http://python.org) otherwise).  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

---

| tag | date | title |
|---|---|---|
| v2.2.2 | 2017-11-19 | v2.2.2: better handling of multi-org syncs |

These release notes apply to v2.2.2 of 2017-11-19.

## New Features

[#294](https://github.com/adobe-apiplatform/user-sync.py/issues/294): Show statistics about users added to secondaries.

## Bug Fixes

[#283](https://github.com/adobe-apiplatform/user-sync.py/issues/283): Don't import keyring unless needed.

[#286](https://github.com/adobe-apiplatform/user-sync.py/issues/286): Allow specifying attributes for Adobe IDs.

[#288](https://github.com/adobe-apiplatform/user-sync.py/issues/288): Escape special characters in user input to LDAP queries.

[#293](https://github.com/adobe-apiplatform/user-sync.py/issues/293): Don't crash when existing users are added to secondaries.

[#301](https://github.com/adobe-apiplatform/user-sync.py/issues/301): User Sync fails when adding more than 10 groups to a user.

## Compatibility with Prior Versions

There are no interface changes from prior versions.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release (see the setup.py file for the specific version).  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available for that platform (from the OS vendor, if they provide one, from [python.org](http://python.org) otherwise).  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

---

| tag | date | title |
|---|---|---|
| v2.2.2rc3 | 2017-11-14 | Third release candidate for v2.2.2 |

These notes apply to v2.2.2rc3 of 2017-11-14.

## New Features

[#294](https://github.com/adobe-apiplatform/user-sync.py/issues/294): Show statistics about users added to secondaries.

## Bug Fixes

[#283](https://github.com/adobe-apiplatform/user-sync.py/issues/283): Don't import keyring unless needed.

[#286](https://github.com/adobe-apiplatform/user-sync.py/issues/286): Allow specifying attributes for Adobe IDs.

[#288](https://github.com/adobe-apiplatform/user-sync.py/issues/288): Escape special characters in user input to LDAP queries.

[#293](https://github.com/adobe-apiplatform/user-sync.py/issues/293): Don't crash when existing users are added to secondaries.

[#301](https://github.com/adobe-apiplatform/user-sync.py/issues/301): User Sync fails when adding more than 10 groups to a user.

## Compatibility with Prior Versions

There are no interface changes from prior versions.

## Known Issues

The nosetests are broken in this release candidate.

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available (from the OS vendor, if they provide one) for that platform.  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

---

| tag | date | title |
|---|---|---|
| v2.2.2rc2 | 2017-10-29 | Second release candidate for v2.2.2 |

These notes apply to v2.2.2rc2 of 2017-10-29.

## New Features

[#294](https://github.com/adobe-apiplatform/user-sync.py/issues/294): Show statistics about users added to secondaries.

## Bug Fixes

[#283](https://github.com/adobe-apiplatform/user-sync.py/issues/283): Don't import keyring unless needed.

[#286](https://github.com/adobe-apiplatform/user-sync.py/issues/286): Allow specifying attributes for Adobe IDs.

[#288](https://github.com/adobe-apiplatform/user-sync.py/issues/288): Escape special characters in user input to LDAP queries.

[#293](https://github.com/adobe-apiplatform/user-sync.py/issues/293): Don't crash when existing users are added to secondaries.

## Compatibility with Prior Versions

There are no interface changes from prior versions.

## Known Issues

The nosetests are broken in this release candidate.

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available (from the OS vendor, if they provide one) for that platform.  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

---

| tag | date | title |
|---|---|---|
| v2.2.2rc1 | 2017-10-25 | First release candidate for v2.2.2 |

These notes apply to v2.2.2rc1 of 2017-10-25.

## New Features

None.

## Bug Fixes

[#283](https://github.com/adobe-apiplatform/user-sync.py/issues/283): Don't import keyring unless needed.

[#286](https://github.com/adobe-apiplatform/user-sync.py/issues/286): Allow specifying attributes for Adobe IDs.

[#288](https://github.com/adobe-apiplatform/user-sync.py/issues/288): Escape special characters in user input to LDAP queries.

## Compatibility with Prior Versions

There are no interface changes from prior versions.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available (from the OS vendor, if they provide one) for that platform.  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.

---

| tag | date | title |
|---|---|---|
| v2.2.1 | 2017-08-29 | User Sync v2.2.1 - bug fix release |

These notes apply to v2.2.1 of 2017-08-30.

## New Features

[#266](https://github.com/adobe-apiplatform/user-sync.py/issues/266): Extended attribute values (defined in extensions) can now be multi-valued.  The type of the attribute value in the `source_attributes` dictionary will be:
* `None` if the attribute has no value;
* a `str` (or `unicode` in py2) if the attribute has one value;
* a `list` of `str` (or `unicode` in py2) if the attribute has multiple values.

[#268](https://github.com/adobe-apiplatform/user-sync.py/issues/268): To make sure users get all the right overlapping entitlements associated with mapped user groups, `--strategy push` now does group removals before group adds.

## Bug Fixes

[#257](https://github.com/adobe-apiplatform/user-sync.py/issues/257): Catch exceptions thrown by umapi-client when creating actions.

[#258](https://github.com/adobe-apiplatform/user-sync.py/issues/258): Correctly decrypt private keys in py3.

[#260](https://github.com/adobe-apiplatform/user-sync.py/issues/260): Make sure the requests library is loaded when using pex on Windows.

[#265](https://github.com/adobe-apiplatform/user-sync.py/issues/265): Extended attributes in extensions couldn't be fetched unless they had non-ascii names.

[#269](https://github.com/adobe-apiplatform/user-sync.py/issues/269): When using `--strategy sync`, new users created in secondary organizations were not being added to any groups.

## Compatibility with Prior Versions

There are no functional changes from prior versions.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

On Win64, this release was built with and is only guaranteed to work with Python Win64 2.7.13.  We have had reports that it will *not* work with Python Win64 2.7.14, recently released.  Earlier Win64 versions of Python have been observed to work (in particular, 2.7.9 and 2.7.12).

---

| tag | date | title |
|---|---|---|
| v2.2.1rc1 | 2017-08-28 | First release candidate for User Sync 2.2.1 |

# Release Notes for User Sync Tool Version 2.2.1

These notes apply to v2.2.1rc1 of 2017-08-28.

## New Features

[#266](https://github.com/adobe-apiplatform/user-sync.py/issues/266): Extended attribute values (defined in extensions) can now be multi-valued.  The type of the attribute value in the `source_attributes` dictionary will be:
* `None` if the attribute has no value;
* a `str` (or `unicode` in py2) if the attribute has one value;
* a `list` of `str` (or `unicode` in py2) if the attribute has multiple values.

## Bug Fixes

[#257](https://github.com/adobe-apiplatform/user-sync.py/issues/257): Catch exceptions thrown by umapi-client when creating actions.

[#258](https://github.com/adobe-apiplatform/user-sync.py/issues/258): Correctly decrypt private keys in py3.

[#260](https://github.com/adobe-apiplatform/user-sync.py/issues/260): Make sure the requests library is loaded when using pex on Windows.

[#265](https://github.com/adobe-apiplatform/user-sync.py/issues/265): Extended attributes in extensions couldn't be fetched unless they had non-ascii names.

## Compatibility with Prior Versions

There are no functional changes from prior versions.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

---

| tag | date | title |
|---|---|---|
| v2.2 | 2017-07-13 | User Sync v2.2 |

# Release Notes for User Sync Version 2.2

These notes apply to the User Sync Tool (UST) v2.2 of 2017-07-13.

## New Features

[#52](https://github.com/adobe-apiplatform/user-sync.py/issues/52): This release runs on both Python 2 and Python 3 (2.7, 3.4, 3.5, and 3.6 to be precise)!

[#182](https://github.com/adobe-apiplatform/user-sync.py/issues/182): At long last, you can select users in nested groups.  The new implementation for determining group members also allows us to avoid fetching the entire directory when the users are only supposed to come from specific groups, as with `--users mapped` ([#129](https://github.com/adobe-apiplatform/user-sync.py/issues/129)).  There is a new LDAP configuration setting `group_member_filter_format` which controls how users are selected for groups (default is "immediate members only", which is backward compatible with prior releases).

[#236](https://github.com/adobe-apiplatform/user-sync.py/issues/236): Directory users can now be pushed directly to Adobe, rather than synchronized with a fetch of Adobe users.  A new command-line argument `--strategy push` (as opposed to the default `--strategy sync`) controls this.

[#234](https://github.com/adobe-apiplatform/user-sync.py/issues/234): There are new UMAPI configuration settings (`timeout` and `retries` in the `server` section) to control the network behavior when talking to the UMAPI server.  The default timeout of 120 seconds and the default retry count of 3 are unchanged.

[#237](https://github.com/adobe-apiplatform/user-sync.py/issues/237): The default encoding for all inputs (config files, CSV files, LDAP attribute values) is now assumed to be `utf8` rather than ASCII.  This is a backward-compatible change that makes it unnecessary (but still allowed) to specify `utf8` explicitly.

## Bug Fixes

[#227](https://github.com/adobe-apiplatform/user-sync.py/issues/227): Fixed crashes due to bad user keys.

[#233](https://github.com/adobe-apiplatform/user-sync.py/issues/233): Exceptions in LDAP connections are handled gracefully, as are keyboard interrupts.

[#235](https://github.com/adobe-apiplatform/user-sync.py/issues/235): Fixed a crash that occurred if an Adobe ID user had no username or domain info.

[#240](https://github.com/adobe-apiplatform/user-sync.py/issues/240): When using the LDAP connector, the domain of each user is now correctly defaulted to the email domain.

[#244](https://github.com/adobe-apiplatform/user-sync.py/issues/244): Build instructions are now provided for all platforms, and the default `Makefile` allows for the use of pre-compiled, platform-specific wheels.

[#247](https://github.com/adobe-apiplatform/user-sync.py/issues/247): There is no more use of the `uid` attribute in LDAP directories.

[#254](https://github.com/adobe-apiplatform/user-sync.py/issues/254): Update windows libraries, reduce use of custom builds.

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.1.  As mentioned above, there are new configuration settings for filtering group members and controlling network behavior, and there is a new command-line option for controlling the update strategy.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py) for full details about configuration.

**LDAP usage change**: Prior releases of User Sync did *not* run LDAP queries to get the members of groups.  With the release of version 2.2's support for [nested groups](https://github.com/adobe-apiplatform/user-sync.py/issues/182), we now run LDAP queries for group membership (both direct and nested).  This requires that the LDAP account used by the tool to have a security profile that allows use of `memberOf` queries.

## Known Issues

If prior versions of User Sync were correctly returning the right members of LDAP groups, but the current version returns no members for those groups, you are probably using an LDAP account that is not enabled for `memberOf` queries.  See the note above about _LDAP usage change_.

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

---

| tag | date | title |
|---|---|---|
| v2.2rc2 | 2017-06-26 | Second release candidate for v2.2 |

These notes apply to v2.2rc2 of 2017-06-26.

## New Features

[#52](https://github.com/adobe-apiplatform/user-sync.py/issues/52): This release runs on both Python 2 and Python 3 (2.7, 3.4, 3.5, and 3.6 to be precise)!

[#182](https://github.com/adobe-apiplatform/user-sync.py/issues/182): At long last, you can select users in nested groups.  The new implementation for determining group members also allows us to avoid fetching the entire directory when the users are only supposed to come from specific groups, as with `--users mapped` ([#129](https://github.com/adobe-apiplatform/user-sync.py/issues/129)).  There is a new LDAP configuration setting `group_member_filter_format` which controls how users are selected for groups (default is "immediate members only", which is backward compatible with prior releases).

[#236](https://github.com/adobe-apiplatform/user-sync.py/issues/236): Directory users can now be pushed directly to Adobe, rather than synchronized with a fetch of Adobe users.  A new command-line argument `--strategy push` (as opposed to the default `--strategy sync`) controls this.

[#234](https://github.com/adobe-apiplatform/user-sync.py/issues/234): There are new UMAPI configuration settings (`timeout` and `retries` in the `server` section) to control the network behavior when talking to the UMAPI server.  The default timeout of 120 seconds and the default retry count of 3 are unchanged.

[#237](https://github.com/adobe-apiplatform/user-sync.py/issues/237): The default encoding for all inputs (config files, CSV files, LDAP attribute values) is now assumed to be `utf8` rather than ASCII.  This is a backward-compatible change that makes it unnecessary (but still allowed) to specify `utf8` explicitly.

## Bug Fixes

[#227](https://github.com/adobe-apiplatform/user-sync.py/issues/227): Fixed crashes due to bad user keys.

[#233](https://github.com/adobe-apiplatform/user-sync.py/issues/233): Exceptions in LDAP connections are handled gracefully, as are keyboard interrupts.

[#235](https://github.com/adobe-apiplatform/user-sync.py/issues/235): Fixed a crash that occurred if an Adobe ID user had no username or domain info.

[#240](https://github.com/adobe-apiplatform/user-sync.py/issues/240): When using the LDAP connector, the domain of each user is now correctly defaulted to the email domain.

[#244](https://github.com/adobe-apiplatform/user-sync.py/issues/244): Build instructions are now provided for all platforms, and the default `Makefile` allows for the use of pre-compiled, platform-specific wheels.

[#247](https://github.com/adobe-apiplatform/user-sync.py/issues/247): There is no more use of the `uid` attribute in LDAP directories.

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.1.  As mentioned above, there are new configuration settings for filtering group members and controlling network behavior, and there is a new command-line option for controlling the update strategy.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py) for full details about configuration.

## Known Issues

Because the releases on Windows are built with pre-compiled dependencies, we have to lock down the versions of pycryptodome and PyYAML used in each release.  Thus they may not always be the latest version (as, for example, with this release, which uses pycryptodome 2.4.35.1 rather than 2.4.36).

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

---

| tag | date | title |
|---|---|---|
| v2.2rc1 | 2017-06-20 | First candidate build for v2.2 |

These notes apply to v2.2rc1 of 2017-06-20.

## New Features

#52: This release runs on both Python 2 and Python 3 (2.7, 3.4, 3.5, and 3.6 to be precise)!

#234: There are new UMAPI configuration settings (`timeout` and `retries` in the `server` section) to control the network behavior when talking to the UMAPI server.  The default timeout of 120 seconds and the default retry count of 3 are unchanged.

#182: At long last, you can select users in nested groups.  The new implementation also allows us to avoid fetching the entire directory when the users are only supposed to come from specific groups, as with `--users mapped` (#129).

#236: Directory users can now be pushed directly to Adobe, rather than synchronized with a fetch of Adobe users.  A new command-line argument `--strategy push` (as opposed to the default `--strategy sync`) controls this.

#237: The default encoding for all inputs (config files, CSV files, LDAP attribute values) is now assumed to be `utf8` rather than ASCII.  This is a backward-compatible change that makes it unnecessary (but still allowed) to specify `utf8` explicitly.

## Bug Fixes

This release contains bug fixes for:

* #227: crashes due to bad user keys.
* #235: crash if Adobe ID user has no username or domain info.
* #233: exceptions in LDAP connections are handled gracefully, as are keyboard interrupts.

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.1.  As mentioned above, there are new configuration settings for controlling network behavior and update strategy.

## Known Issues

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

## Builds

Premade builds for this release may be a little slow in appearing, as we figure out exactly which set of builds we are going to make for which platforms.

---

| tag | date | title |
|---|---|---|
| v2.1.1 | 2017-06-09 | User Sync version 2.1.1 |

These release notes apply to v2.1.1 of 2017-06-09.

## New Features

To address [Issue 198](https://github.com/adobe-apiplatform/user-sync.py/issues/198), we have added support for [private key encryption](https://github.com/kjur/jsrsasign/wiki/Tutorial-for-PKCS5-and-PKCS8-PEM-private-key-formats-differences) in both PKCS#5 and PKCS#8 formats, and allowed the passphrase for an encrypted private key to be stored in the platform secure credential store.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/) for details on the new feature.

## Bug Fixes

There is one fix for some obscure Unicode edge cases (that were found only by code inspection): [Issue 167](https://github.com/adobe-apiplatform/user-sync.py/issues/167).

User Sync no longer crashes if a user's LDAP email address is present but empty: [Issue 201](https://github.com/adobe-apiplatform/user-sync.py/issues/201).

The proper packages were not present for secure credential storage on Linux platforms: [Issue 199](https://github.com/adobe-apiplatform/user-sync.py/issues/199).

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.

There are new UMAPI config file settings in this release to enable the use of encrypted keys, see [this section of the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/deployment_best_practices.html#storing-credentials-in-os-level-storage) for full details.

## Known Issues

On the Win64 platform, due to a change in the encryption support library used by User Sync, there are very long pathnames embedded in the released build artifact `user-sync.pex`.  It will likely be necessary to set the `PEX_ROOT` environment variable on Windows (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `env:$PEX_ROOT="C:\pex"`) in order to launch User Sync successfully.  We hope to avoid the need for this workaround in a future release.

---

| tag | date | title |
|---|---|---|
| v2.1.1rc2 | 2017-06-07 | second release candidate of v2.1.1 |

This release should be code-complete for v2.1.1, and includes a live push of the docs.

**BUILD NOTE**: If you build this release yourself, you will need a fresh python environment that doesn't include `pycrypto` (which we used to use).  We have moved to `pycryptodome` which is a more modern, well-maintained plug-compatible module.

# Release Notes for User Sync Tool Version 2.1.1

These notes apply to v2.1.1rc2 of 2017-06-07.

## New Features

To address [Issue 198](https://github.com/adobe-apiplatform/user-sync.py/issues/198), we have added support for [private key encryption](https://github.com/kjur/jsrsasign/wiki/Tutorial-for-PKCS5-and-PKCS8-PEM-private-key-formats-differences) in both PKCS#5 and PKCS#8 formats, and allowed the passphrase for an encrypted private key to be stored in the platform secure credential store.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/) for details on the new feature.

## Bug Fixes

There is one fix for some obscure Unicode edge cases (that were found only by code inspection): [Issue 167](https://github.com/adobe-apiplatform/user-sync.py/issues/167).

User Sync no longer crashes if a user's LDAP email address is present but empty: [Issue 201](https://github.com/adobe-apiplatform/user-sync.py/issues/201).

The proper packages were not present for secure credential storage on Linux platforms: [Issue 199](https://github.com/adobe-apiplatform/user-sync.py/issues/199).

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.

---

| tag | date | title |
|---|---|---|
| v2.1.1rc1 | 2017-06-06 | First release candidate for 2.1.1rc1 |

v2.1.1 is planned as a bug-fix release.  This is the first release candidate.

---

| tag | date | title |
|---|---|---|
| v2.1 | 2017-05-11 | Enhancement Release: unicode and security |

1. We now have full Unicode support.  See [Issue 167](https://github.com/adobe-apiplatform/user-sync.py/issues/167) for details, including the new `--config-file-encoding` command-line option.
2. We now support secure handling for all credential settings and credential files.  See [Issue 159](https://github.com/adobe-apiplatform/user-sync.py/issues/159) for design discussion, and read [the docs](https://adobe-apiplatform.github.io/user-sync.py/) for associated config changes.

NOTE: This release is stable and can be used reliably by customers who need the additional security or unicode features.  We have left the pre-release flag on because customers have discovered issues on Linux and Windows with security (#199, #198).  We will issue a double-dot that fixes these issues.

---

| tag | date | title |
|---|---|---|
| v2.1rc2 | 2017-05-11 | Second release candidate for v2.1 |

The base functionality of rc1 is stable, but there have been some server-side behavior changes we need to accommodate (see #189), and we want to eke out a bit more debugging info when requests fail on the server side (see #181). This release does that.

---

| tag | date | title |
|---|---|---|
| v2.1rc1 | 2017-05-05 | 1st release candidate: security and unicode enhancements |

1. We now have full Unicode support.  See [Issue 167](https://github.com/adobe-apiplatform/user-sync.py/issues/167) for details, including the new `--config-file-encoding` command-line option.
2. We now support secure handling for all credential settings and credential files.  See [Issue 159](https://github.com/adobe-apiplatform/user-sync.py/issues/159) for design discussion, and read [the docs](https://adobe-apiplatform.github.io/user-sync.py/) for associated config changes.

---

| tag | date | title |
|---|---|---|
| v2.0 | 2017-04-10 | User Sync version 2.0 |

This is the 2.0 release of User Sync from Adobe.  This release has extensive feature and performance enhancements and, while it can be configured so as to have the same function as prior releases, its default invocation and configuration behavior is *not* backwards compatible.  Please read these release notes carefully, and refer to the [complete documentation](https://adobe-apiplatform.github.io/user-sync.py/) for details.

## New Arguments & Configuration Syntax

There has been an extensive overhaul of both the configuration file syntax and the command-line argument syntax.  See [Issue 95](https://github.com/adobe-apiplatform/user-sync.py/issues/95) and the [docs](https://adobe-apiplatform.github.io/user-sync.py/) for details.

## New Features

1. You can now exclude Adobe users from being updated or deleted by User Sync. See the [docs](https://adobe-apiplatform.github.io/user-sync.py/) for details.
2. There is more robust reporting for errors in configuration files.
3. The log now reports the User Sync version and gives the details of how it was invoked.
4. You can now create and manage users of all identity types, including Adobe IDs, both when operating from an LDAP directory and from CSV files.
5. You can now distinguish, when a customer directory user is disabled or removed, whether to remove the matching Adobe-side user's product configurations and user groups, to remove the user but leave his cloud storage, or to delete his storage as well.
   
## Significant Bug Fixes

1. There were many bugs fixed related to managing users of identity types other than Federated ID.
2. There were many bugs fixes related to managing group membership of all identity types.
3. There was a complete overhaul of how users who have adobe group memberships in multiple organizations are managed.

## Changes in Behavior

All options now apply to users of all identity types. Previously, some had applied only to Federated ID and some to Enterprise ID.

## Compatibility with Prior Versions

All existing configuration files, user input files, and command-line scripts will need to be revamped to be compatible with the new formats.  Here is a quick cheat sheet of what needs to be done.

### Configuration Files

* replace `dashboard:` with `adobe_users:`
* replace `directory:` with `directory_users:`
* add a `connectors:` section under `adobe_users:` similar to the one under `directory_users`
* change `owning` to be `umapi` and put it under `connectors`
* if you access multiple organizations, remove `secondaries`, and put all the umapi specifications under `umapi` as a list, like this:
```yaml
adobe_users:
  connectors:
    umapi:
      - primary-config.yml
      - org1: org1-config.yml
      - org2: org2-config.yml
```
* change `dashboard_groups` to `adobe_groups`
* under `limits`, change `max_missing_users` to `max_adobe_only_users` and remove all other settings
* if you have an extension, do the following:
  * remove the per-context: user setting
  * move all the settings under it to the top level in a new file, call it `extension.yaml`
  * change `extensions` to `extension`, move it into the `directory_users` section, and put the relative path to the new `extension.yaml` file as its value.

### User Input Files

If you have a file that lists users for input (`--users file` _f_), the column head `user` should be changed to `username`.

### Removed User Input Files

The format for files containing users to be removed/deleted has changed, and you will need to regenerate these files rather than using any existing ones.

### Command Line Scripts

* All of the options related to Adobe user removal have been changed to use the new `--adobe-only-user-action` argument.
* The `--source-filter` argument has been removed.  Use the configuration setting `all_users_filter` instead.

---

| tag | date | title |
|---|---|---|
| v2.0rc2 | 2017-04-07 | Second release candidate for v2.0 |

There were a few bugs found, mostly cosmetic, since the v2.0rc1 release, and there have been a lot of doc updates.  We decided to do an rc2 to give users outside the development team more time to test.  As with the rc1 build, please be sure to read the [release notes](https://github.com/adobe-apiplatform/user-sync.py/blob/v2/RELEASE_NOTES.md) and the [updated docs](https://adobe-apiplatform.github.io/user-sync.py/) for info about all of the changes in config file format and invocation arguments.

---

| tag | date | title |
|---|---|---|
| v2.0rc1 | 2017-04-04 | First release candidate for version 2.0 |

Testing on the alpha build went every well, and this build has all known issues resolved.  It should be ready for widespread testing.  Please be sure to read the [release notes](https://github.com/adobe-apiplatform/user-sync.py/blob/v2/RELEASE_NOTES.md) and the [updated docs](https://adobe-apiplatform.github.io/user-sync.py/) for info about all of the changes in config file format and invocation arguments.

---

| tag | date | title |
|---|---|---|
| v2.0a1 | 2017-04-03 | Internal 2.0 alpha 1 build |

Nosetests don't work, but functionality should.

---

| tag | date | title |
|---|---|---|
| v1.2rc2 | 2017-03-24 | Second release candidate for 1.2 |

Important Note: We will be dropping the 1.2 release in favor of 2.0.  Any further testing should move there.

Note: This build is for testing purposes only.  It should NOT be distributed to customers nor used for production work.  

This has all the features and bug fixes comleted and seems quite stable.  Items to take special note of, because these affect the invocation args and configuration files:

* All pathnames found in config files are now interpreted relative to the file that contains them (full fix of #30).  This means you can put the config file anywhere, and it can refer to files relative to its location (e.g., it can refer to the connector configs via relative pathnames), and then the referred to files can refer to other files relative to their location (e.g., a connector config could refer relatively to a private key file).
* There has been a rename of arguments so that, instead of referring to `nonexistent-users` (whatever those are), we talk about `unmatched-users` (that is, users on the Adobe side that have no match on the customer side).  You can now specify any one of the following processing args for unmatched users:
`--remove-entitlements-for-unmatched-users`, `--remove-unmatched-users`, or `--delete-unmatched users`.  (_*Note*_ that there is still some debate about this renaming, so it's possible the arg names will go back to what they were in the GM build.)
* We used to have separate arguments for outputting unmatched users to or inputting unmatched users from a file, one for each kind of processing (remove-entitlements vs remove vs delete).  These have been collapsed into just two: they are now `--output-unmatched-users` (to write the file) and `--input-unmatched-users` (to read the file).
* The limits settings on processing unmatched users have changed: they are now `max_unmatched_users` (used to be `max_missing_users`) and `max_removed_users` (used to be `max_deletions_per_run`).

A lot of the underlying processing related to the various removal options for users has been overhauled and made way more consistent and efficient, especially in those cases where you have accessor orgs as well as an owning organization.  In all cases, the code now assumes that only those users in the owning organization are to be matched against customer users (and controlled by the `exclude` settings), and the accessor orgs are never used except to update group mappings (or do org removal).  The attributes in accessor orgs are never consulted or updated, and we never consider or touch users in those orgs other than the ones that are also in the owning org.

Unless we find problems between now and end-of-day Monday 27 March, expect the final release to come Tuesday morning, 28 March.

---

| tag | date | title |
|---|---|---|
| v1.2rc1 | 2017-03-20 | First release candidate for v1.2 |

Putting this out for widespread testing.  These notes apply to 1.2rc1 of 2017-03-20.

## New Features

1. You can now exclude dashboard users from being updated or deleted by User Sync. See the [docs](https://adobe-apiplatform.github.io/user-sync.py/) for details.
2. There is more robust reporting for errors in configuration files.
3. The log now reports the User Sync version and gives the details of how it was invoked.
4. You can now create and manage users of all identity types, including Adobe IDs, both when operating from an LDAP directory and from CSV files.
5. You can now distinguish, when a customer directory user is disabled or removed, whether to remove the matching Adobe-side from the organization or also to delete his Adobe user account.
   
## Significant Bug Fixes

1. There were many bugs fixed related to managing users of identity types other than Federated ID.
2. There were many bugs fixes related to managing group membership of all identity types.

## Changes in Behavior

All options now apply to users of all identity types. Previously, some had applied only to Federated ID and some to Enterprise ID.

## Compatibility with Prior Versions

Other than as noted above, existing configuration files and should work and have the same behavior.

---

| tag | date | title |
|---|---|---|
| v1.1.1-with-docs | 2017-03-03 | v1.1.1 with documentation |

Fast-follow bug fix release that fixes #26 and updates the version number. See the detailed [Release Notes](https://github.com/adobe-apiplatform/user-sync.py/blob/v1.1.1-with-docs/RELEASE_NOTES.md) online, or download them from the release artifacts.

There are known issues with this release related to creating/syncing users identified by Adobe ID, but these will not affect users working exclusively with Enterprise and Federated IDs.

There are no code changes in this release since the v1.1.1 tag on Master, so if you already downloaded the sources at that tag, you need _not_ download and rebuild.

---

| tag | date | title |
|---|---|---|
| v1.1 | 2017-03-01 | v1.1 |

Enhancements and bug fixes since v1.0: see the RELEASE_NOTES.md file.

---

| tag | date | title |
|---|---|---|
| v1.0 | 2017-02-03 | First GM release |

This release still has [issues](https://github.com/adobe-apiplatform/user-sync.py/issues) but should be usable for most customers.  There is an updated User Guide in the docs directory.

---

| tag | date | title |
|---|---|---|
| v1.0rc1 | 2017-01-20 | First release candidate for first public release |

Have preliminary doc and code seems to be ready.
