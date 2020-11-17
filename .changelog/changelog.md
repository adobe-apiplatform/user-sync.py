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
