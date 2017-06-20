# Release Notes for User Sync Tool Version 2.1.1

These notes apply to v2.2rc1 of 2017-06-18.

## New Features

[#52](https://github.com/adobe-apiplatform/user-sync.py/issues/235): This release runs on both Python 2 and Python 3 (2.7, 3.4, 3.5, and 3.6 to be precise)!

[#234](https://github.com/adobe-apiplatform/user-sync.py/issues/234): There are new UMAPI configuration settings (`timeout` and `retries` in the `server` section) to control the network behavior when talking to the UMAPI server.  The default timeout of 120 seconds and the default retry count of 3 are unchanged.

[#182](https://github.com/adobe-apiplatform/user-sync.py/issues/182): At long last, you can select users in nested groups.  The new implementation also allows us to avoid fetching the entire directory when the users are only supposed to come from specific groups, as with `--users mapped` ([#129](https://github.com/adobe-apiplatform/user-sync.py/issues/129).

[#236](https://github.com/adobe-apiplatform/user-sync.py/issues/236): Directory users can now be pushed directly to Adobe, rather than synchronized with a fetch of Adobe users.  A new command-line argument `--strategy push` (as opposed to the default `--strategy sync`) controls this.

## Bug Fixes

This release contains bug fixes for:

* [#227](https://github.com/adobe-apiplatform/user-sync.py/issues/227): crashes due to bad user keys.
* [#235](https://github.com/adobe-apiplatform/user-sync.py/issues/235): crash if Adobe ID user has no username or domain info.
* [#233](https://github.com/adobe-apiplatform/user-sync.py/issues/233): exceptions in LDAP connections are handled gracefully, as are keyboard interrupts.

## Compatibility with Prior Versions

This version is fully backwards-compatible with version 2.1.1.  As mentioned above, there are new configuration settings for controlling network behavior and update strategy.

## Known Issues

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).
