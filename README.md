# user-sync.py

Application for synchronizing customer directories with the
Adobe Enterprise Admin Console via the
[User Management API](https://www.adobe.io/products/usermanagement/docs/gettingstarted.html)
(aka UMAPI).

This application is open source, maintained by Adobe, and distributed under the terms
of the OSI-approved MIT license.  See the LICENSE file for details.

Copyright (c) 2016-2017 Adobe Systems Incorporated.

# Overview

`user-sync` automates user creation and product entitlement
assignment in the Adobe Enterprise Admin Console.
It takes a list of enterprise directory users, 
either from an LDAP connection or from a tab-separated file, 
and creates, updates, or removes user accounts in the
Admin Console.

# Requirements

* Python 2.7+
* User Management API Credentials (see [the official documentation](https://www.adobe.io/products/usermanagement/docs/gettingstarted))
* Accessible LDAP server (optional)
* If running on Windows, a 64 bit version of Windows is required.

# Installation

The connector is packaged as a [self-contained .pex file](https://github.com/pantsbuild/pex).  See the releases page to get the latest build for your platform.

## Build Instructions

Requirements:

* Python 2.7+
* [virtualenv](https://virtualenv.pypa.io/en/stable/)
* If building on Debian - `python-dev libssl-dev libffi-dev libsasl2-dev libldap2-dev`
* GNU Make

To build, run `make pex` from the command line in the main repo directory.

## Build Instructions for local execution and debugging on Windows

Builds and execution are setup for 64 bit windows versions.

First, there are several projects that do not have good 64 bit builds for Windows platforms.  These are enum34, python_ldap, and pyYaml.  Acceptable builds are in the misc/build/Win64 folder and these can be used directly.  You can also check http://www.lfd.uci.edu/~gohlke/pythonlibs/

Load dependencies into interpreter directory:
    
	pip install -r misc\build\Win64\python-ldap-requirements.txt
  pip install -r misc\build\requirements.txt

The requirements will usually be loaded into C:\Python27\lib\site-packages if C:\Python27 is your install directory and you aren't specifying any options that send things elsewhere.

To set up PyCharm for debugging, 
1. Make sure you are using 64 bit python interpreter.  File Settings Project Interpreter
2. Make sure interprter isn't overridden in run configuration
3. Set up a run configuration based on Python that references the user_sync\app.py file as the script, and has the command line parameters you want to test with (e.g. --users file test.csv).  Working directory works best as the folder with your config files.

# Basic Usage

```
Adobe Enterprise Dashboard User Sync

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -t, --test-mode       run API action calls in test mode (does not execute
                        changes). Logs what would have been executed.
  -c path, --config-path path
                        specify path to config files. (default: "")
  --config-filename filename
                        main config filename. (default: "user-sync-
                        config.yml")
  --users all|file|mapped|group [arg1 ...]
                        specify the users to be considered for sync. Legal
                        values are 'all' (the default), 'group name or names'
                        (one or more specified groups), 'mapped' (all groups
                        listed in configuration file), 'file f' (a specified
                        input file).
  --user-filter pattern
                        limit the selected set of users that may be examined
                        for syncing, with the pattern being a regular
                        expression.
  --source-filter connector:file
                        send the file to the specified connector (for example,
                        --source-filter ldap:foo.yml). This parameter is used
                        to limit the scope of the LDAP query.
  --update-user-info    if user information differs between the customer side
                        and the Adobe side, the Adobe side is updated to
                        match.
  --process-groups      if the membership in mapped groups differs between the
                        customer side and the Adobe side, the group membership
                        is updated on the Adobe side so that the memberships
                        in mapped groups matches the customer side.
  --remove-nonexistent-users
                        Causes the user sync tool to remove users that exist on
                        the Adobe side if they are not in the customer side
                        directory.
  --generate-remove-list output_path
                        processing similar to --remove-nonexistent-users
                        except that rather than performing removals, a file is
                        generated (with the given pathname) listing users who
                        would be removed. This file can then be given in the
                        --remove-list argument in a subsequent run.
  --remove-list input_path
                        specifies the file containing the list of users to be
                        removed. Users on this list are removed from the 
                        organization on the Adobe side.
  --delete-nonexistent-users
                        Causes the user sync tool to delete user accounts on
                        the Adobe side if they are not in the customer side
                        directory. Adobe ID user accounts are removed from the
                        organization, but not deleted.
  --generate-delete-list output_path
                        processing similar to --delete-nonexistent-users
                        except that rather than performing removals, a file is
                        generated (with the given pathname) listing users who
                        would be removed. This file can then be given in the
                        --delete-list argument in a subsequent run.
  --delete-list input_path
                        specifies the file containing the list of users to be
                        deleted. Enterprise and federated users on this list
                        are deleted on the Adobe side, and Adobe ID users are
                        removed from the organization but not deleted.
```

# Configuration

See `examples/example.user-sync-config.yml` for the main configuration template.  The main configuration file user-sync-config.yml must exist in the configuration path.

See `examples/example.dashboard-config.yml` for the dashboard configuration template.  The tool would try and find dashboard-owning-config.yml in the configuration path.

See `examples/example.connector-ldap.yml` for the ldap configuration template.  The main configuration file can be configured to reference this file.


