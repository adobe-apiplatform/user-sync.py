# Release Notes for User Sync Tool Version 2.2.1

These notes apply to v2.2.1rc1 of 2017-08-28.

## New Features

[#266](https://github.com/adobe-apiplatform/user-sync.py/issues/266): Extended attribute values (defined in extensions) can now be multi-valued.  The type of the attribute value in the `source_attributes` dictionary will be:
* `None` if the attribute has no value;
* a `str` (or `unicode` in py2) if the attribute has one value;
* a `list` of `str` (or `unicode` in py2) if the attribute has multiple values.

## Bug Fixes

[#257](https://github.com/adobe-apiplatform/user-sync.py/issues/257): Catch exceptions thrown by umapi-client when creating actions.

[#258](https://github.com/adobe-apiplatform/user-sync.py/issues/258): Correctly decrypte private keys in py3.

[#260](https://github.com/adobe-apiplatform/user-sync.py/issues/260): Make sure the requests library is loaded when using pex on Windows.

[#265](https://github.com/adobe-apiplatform/user-sync.py/issues/265): Extended attributes in extensions couldn't be fetched unless they had non-ascii names.

## Compatibility with Prior Versions

There are no functional changes from prior versions.

## Known Issues

Because the release on Windows is built with a pre-compiled version of pyldap, we have to specify a specific version to be used in each release.  This not always be the latest version.

On the Win64 platform, there are very long pathnames embedded in the released build artifact `user-sync.pex`, which will cause problems unless you are on Windows 10 and are either running Python 3.6 or have enabled long pathnames system-wide (as described in this [Microsoft Dev Center article](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx)).  To work around this issue on older platforms, set the `PEX_ROOT` environment variable (as described [in the docs here](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/setup_and_installation.html)) to be a very short path (e.g., `set PEX_ROOT=C:\pex`).
