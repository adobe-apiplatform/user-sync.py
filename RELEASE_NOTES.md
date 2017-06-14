# Release Notes for User Sync Tool Version 2.1.1

These notes apply to v2.2a1 of 2017-06-13.

## New Features

None.

## Bug Fixes

We have a trial fix for [#227](https://github.com/adobe-apiplatform/user-sync.py/issues/227): crashes due to bad user keys.

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.1.

## Known Issues

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`.  It will likely be necessary to set the `PEX_ROOT` environment variable on Windows (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `env:$PEX_ROOT="C:\pex"`) in order to launch User Sync successfully.  We hope to avoid the need for this workaround in a future release.
