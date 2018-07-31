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
