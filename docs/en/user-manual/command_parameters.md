---
layout: page
lang: en
nav_link: Command Line Parameters
nav_level: 2
nav_order: 40
---


## Command Parameters

Once the configuration files are set up, you can run the User
Sync tool on the command line or in a script. To run the tool,
execute the following command in a command shell or from a
script:

`user-sync` \[ _optional parameters_ \]

The tool accepts optional parameters that determine its
specific behavior in various situations.


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
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;filename<br/><br/>`--adobe-only-user-action  exclude` | When supplied, if user accounts are found on the Adobe side that are not in the directory, take the indicated action.  <br/><br/>`preserve`: no action concerning account deletion is taken. This is the default.  There may still be group membership changes if the `--process-groups` option was specified.<br/><br/>`remove-adobe-groups`: The account is removed from user groups and product configurations, freeing any licenses it held, but is left as an active account in the organization.<br><br/>`remove`: In addition to remove-adobe-groups, the account is also removed from the organization, but the user account, with its associated assets, is left in the domain and can be re-added to the organization if desired.<br/><br/>`delete`: In addition to the action for remove, the account is deleted if its domain is owned by the organization.<br/><br/>`write-file`: No action concerning account deletion is taken. The list of user accounts present on the Adobe side but not in the directory is written to the file indicated.  You can then pass this file to the `--adobe-only-user-list` argument in a subsequent run.  There may still be group membership changes if the `--process-groups` option was specified.<br/><br/>`exclude`: No update of any kind is applied to users found only on the Adobe side.  This is used when doing updates of specific users via a file (--users file f) where only users needing explicit updates are listed in the file and all other users should be left alone.<br/><br>Only permitted actions will be applied.  Accounts of type adobeID are owned by the user so the delete action will do the equivalent of remove.  The same is true of Adobe accounts owned by other organizations. |
| `adobe-only-user-list` _filename_ | Specifies a file from which a list of users will be read.  This list is used as the definitive list of "Adobe only" user accounts to be acted upon.  One of the `--adobe-only-user-action` directives must also be specified and its action will be applied to user accounts in the list.  The `--users` option is disallowed if this option is present: only account removal actions can be processed.  |
{: .bordertablestyle }

---
