# Release Notes for User Sync Tool Version 2.1.1

These notes apply to v2.1.1 of 2017-06-09.

## New Features

To address [Issue 198](https://github.com/adobe-apiplatform/user-sync.py/issues/198), we have added support for [private key encryption](https://github.com/kjur/jsrsasign/wiki/Tutorial-for-PKCS5-and-PKCS8-PEM-private-key-formats-differences) in both PKCS#5 and PKCS#8 formats, and allowed the passphrase for an encrypted private key to be stored in the platform secure credential store.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/) for details on the new feature.

## Bug Fixes

There is one fix for some obscure Unicode edge cases (that were found only by code inspection): [Issue 167](https://github.com/adobe-apiplatform/user-sync.py/issues/167).

User Sync no longer crashes if a user's LDAP email address is present but empty: [Issue 201](https://github.com/adobe-apiplatform/user-sync.py/issues/201).

The proper packages were not present for secure credential storage on Linux platforms: [Issue 199](https://github.com/adobe-apiplatform/user-sync.py/issues/199).

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.

There are new UMAPI config file settings in this release to enable the use of encyrpted keys, see [this section of the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/deployment_best_practices.html#storing-credentials-in-os-level-storage) for full details.

## Known Issues

On the Win64 platform, due to a change in the encryption support library used by User Sync, there are very long pathnames embedded in the released build artifact `user-sync.pex`.  It will likely be necessary to set the `PEX_ROOT` environment variable on Windows (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `env:$PEX_ROOT="C:\pex"`) in order to launch User Sync successfully.  We hope to avoid the need for this workaround in a future release.
