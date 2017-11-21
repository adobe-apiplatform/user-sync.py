# Release Notes for User Sync Tool Version 2.3

These notes apply to v2.3rc1 of 2017-11-20.

## New Features

User Sync can now connect to Okta enterprise directories.  Create an Okta configuration and use the new `--connector okta` command-line argument to select that connector.  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/advanced_configuration.html#the-okta-connector) for details.

There is a new command-line argument `--connector` for specifying whether to get directory information via LDAP file, by reading a CSV file, or via the Okta connector.  The default connector is `ldap`.  For CSV users, who formerly had to specify their input source with the `--users` argument, this optional argument offers the chance to specify `--users mapped` or `--users group ...` (since the CSV input can be specified with `--connector`).  See [the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for details.

## Bug Fixes

[#305](https://github.com/adobe-apiplatform/user-sync.py/issues/305) General issues with Okta connector.

[#306](https://github.com/adobe-apiplatform/user-sync.py/issues/306) v2.2.2 crashes if country code not specified.

## Compatibility with Prior Versions

All configuration and command-line arguments accepted in prior releases work in this release.  The `--users file` argument is still accepted, and is equivalent to (although more limited than) specifying `--connector csv`.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release (see the setup.py file for the specific version).  This may not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).

Each release on each platform is built with a specific version of Python.  Typically this is the latest available for that platform (from the OS vendor, if they provide one, from [python.org](http://python.org) otherwise).  In general, and especially on Windows, you should use the same Python to run User Sync as it was built with.
