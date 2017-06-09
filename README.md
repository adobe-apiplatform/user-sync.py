# user-sync.py: User Sync Tool from Adobe

The User Sync Tool is a command-line tool that automates the creation and management of Adobe user accounts.  It
does this by reading user and group information from an organization's enterprise directory system or a file and 
then creating, updating, or removing user accounts in the Adobe Admin Console. The key goals of the User Sync 
Tool are to streamline the process of named user deployment and automate user management for all Adobe users and products.

This application is open source, maintained by Adobe, and distributed under the terms
of the OSI-approved MIT license.  See the LICENSE file for details.

Copyright (c) 2016-2017 Adobe Systems Incorporated.

# Quick Links

- [User Sync Overview](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/UserSyncTool.html)
- [User Manual](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/)
- [Step-by-Step Setup](https://adobe-apiplatform.github.io/user-sync.py/en/success-guide/)
- [Non-Technical Overview](https://spark.adobe.com/page/E3hSsLq3G1iVz/)


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

## User Sync command line


| Parameters&nbsp;and&nbsp;argument&nbsp;specifications | Description |
|------------------------------|------------------|
| `-h`<br />`--help` | Show this help message and exit.  |
| `-v`<br />`--version` | Show program's version number and exit.  |
| `-t`<br />`--test-mode` | Run API action calls in test mode (does not execute changes). Logs what would have been executed.  |
| `-c` _filename_<br />`--config-filename` _filename_ | The complete path to the main configuration file, absolute or relative to the working folder. Default filename is "user-sync-config.yml" |
| `--users` `all`<br />`--users` `file` _input_path_<br />`--users` `group` _grp1,grp2_<br />`--users` `mapped` | Specify the users to be selected for sync. The default is `all` meaning all users found in the directory. Specifying `file` means to take input user specifications from the CSV file named by the argument. Specifying `group` interprets the argument as a comma-separated list of groups in the enterprise directory, and only users in those groups are selected. Specifying `mapped` is the same as specifying `group` with all groups listed in the group mapping in the configuration file. This is a very common case where just the users in mapped groups are to be synced.|
| `--user-filter` _regex\_pattern_ | Limit the set of users that are examined for syncing to those matching a pattern specified with a regular expression. See the [Python regular expression documentation](https://docs.python.org/2/library/re.html) for information on constructing regular expressions in Python. The user name must completely match the regular expression.|
| `--update-user-info` | When supplied, synchronizes user information. If the information differs between the enterprise directory side and the Adobe side, the Adobe side is updated to match. This includes the firstname and lastname fields. |
| `--process-groups` | When supplied, synchronizes group membership information. If the membership in mapped groups differs between the enterprise directory side and the Adobe side, the group membership is updated on the Adobe side to match. This includes removal of group membership for Adobe users not listed in the directory side (unless the `--adobe-only-user-action exclude` option is also selected).|
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;filename<br/><br/>`--adobe-only-user-action  exclude` | When supplied, if user accounts are found on the Adobe side that are not in the directory, take the indicated action.  <br/><br/>`preserve`: no action concerning account deletion is taken. This is the default.  There may still be group membership changes if the `--process-groups` option was specified.<br/><br/>`remove-adobe-groups`: The account is removed from user groups and product configurations, freeing any licenses it held, but is left as an active account in the organization.<br><br/>`remove`: In addition to remove-adobe-groups, the account is also removed from the organization, but is left as an existing account.<br/><br/>`delete`: In addition to the action for remove, the account is deleted if owned by the organization.<br/><br/>`write-file`: the list of user account present on the Adobe side but not in the directory is written to the file indicated.  No other account action is taken.  You can then pass this file to the `--adobe-only-user-list` argument in a subsequent run.<br/><br/>`exclude`: No update of any kind is applied to users found only on the Adobe side.  This is used when doing updates of specific users via a file (--users file f) where only users needing explicit updates are listed in the file and all other users should be left alone.<br/><br>Only permitted actions will be applied.  Accounts of type adobeID are owned by the user so the delete action will do the equivalent of remove.  The same is true of Adobe accounts owned by other organizations. |
| `adobe-only-user-list` _filename_ | Specifies a file from which a list of users will be read.  This list is used as the definitive list of "Adobe only" user accounts to be acted upon.  One of the `--adobe-only-user-action` directives must also be specified and its action will be applied to user accounts in the list.  The `--users` option is disallowed if this option is present: only account removal actions can be processed.  |
| `--config-file-encoding` _encoding_name_ | Optional.  Specifies the character encoding for the contents of the configuration files themselves.  This includes the main configuration file, "user-sync-config.yml" as well as other configuration files it may reference.  Default is `ascii`.  Character encoding in the user source data (whether csv or ldap) is declared by the connector configurations, and that encoding can be different than the encoding used for the configuration files (e.g., you could have a latin-1 configuration file but a CSV source file that uses utf-8 encoding).  The available encodings are dependent on the Python version used; see the documentation [here](https://docs.python.org/2.7/library/codecs.html#standard-encodings) for more information.  |


# Configuration

See the `examples` directory for sample configuration files of all types.  These sample files include all of the possible options with descriptions of them.
