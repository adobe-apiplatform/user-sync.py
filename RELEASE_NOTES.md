# Release Notes for User Sync Tool Version 2.2

These notes apply to v2.2 of 2017-07-12.

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

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).
