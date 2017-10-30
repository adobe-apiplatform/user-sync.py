# Release Notes for User Sync Tool Version 2.2.2

These notes apply to v2.2.2rc2 of 2017-10-29.

## New Features

None.

## Bug Fixes

[#283](https://github.com/adobe-apiplatform/user-sync.py/issues/283): Don't import keyring unless needed.

[#286](https://github.com/adobe-apiplatform/user-sync.py/issues/286): Allow specifying attributes for Adobe IDs.

[#288](https://github.com/adobe-apiplatform/user-sync.py/issues/288): Escape special characters in user input to LDAP queries.

[#293](https://github.com/adobe-apiplatform/user-sync.py/issues/293): Don't crash when existing users are added to secondaries.

## Compatibility with Prior Versions

There are no interface changes from prior versions.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available (from the OS vendor, if they provide one) for that platform.  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.
