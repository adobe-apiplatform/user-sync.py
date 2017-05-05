# Release Notes for User Sync Tool Version 2.1

These notes apply to v2.1rc1 of 2017-05-05.

## New Features

1. We now have full Unicode support.  See [Issue 167](https://github.com/adobe-apiplatform/user-sync.py/issues/167) for details.
2. We now support secure handling for all credential settings and credential files.  See [Issue 159](https://github.com/adobe-apiplatform/user-sync.py/issues/159) for design discussion, and read [the docs](https://adobe-apiplatform.github.io/user-sync.py/) for associated config changes.

## Compatibility with Prior Versions

This version is fully backward-compatible with version 2.0.  There may be subtle behavioral changes due to bug fixes around support for non-Ascii characters.  There are also new configuration file options and a new command line argument that didn't exist in 2.0.
