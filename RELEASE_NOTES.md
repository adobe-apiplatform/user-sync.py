# Release Notes for User Sync Tool Version 2.1.1

These notes apply to v2.1.1rc1 of 2017-06-06.

## New Features

There are no new features in this release; bug fixes only.

## Bug Fixes

There is one fix for some obscure Unicode edge cases (that were found only by code inspection): [Issue 167](https://github.com/adobe-apiplatform/user-sync.py/issues/167).

User Sync no longer crashes if a user's LDAP email address is present but empty: [Issue 201](https://github.com/adobe-apiplatform/user-sync.py/issues/201).

The proper packages were not present for secure credential storage on Linux platforms: [Issue 199](https://github.com/adobe-apiplatform/user-sync.py/issues/199).

Still to come: a fix for secure key storage on Windows: [Issue 198](https://github.com/adobe-apiplatform/user-sync.py/issues/198).

## Compatibility with Prior Versions

This version is fully backward-compatible with version 2.1.
