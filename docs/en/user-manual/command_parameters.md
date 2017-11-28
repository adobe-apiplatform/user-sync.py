---
layout: default
lang: en
nav_link: Command Parameters
nav_level: 2
nav_order: 40
---


# Command Parameters

---

[Previous Section](configuring_user_sync_tool.md)  \| [Next Section](usage_scenarios.md)

---
Once the configuration files are set up, you can run the User
Sync tool on the command line or in a script. To run the tool,
execute the following command in a command shell or from a
script:

`user-sync` \[ _optional parameters_ \]

The tool accepts optional parameters that determine its
specific behavior in various situations.


| Parameters&nbsp;and&nbsp;argument&nbsp;specifications | Description |
|------------------------------|------------------|
| `-h`<br />`--help` | Show a help message and exit.  |
| `-v`<br />`--version` | Show program's version number and exit.  |
| `-t`<br />`--test-mode` | Run API action calls in test mode (does not execute changes). Logs what would have been executed.  |
| `-c` _filename_<br />`--config-filename` _filename_ | The complete path to the main configuration file, absolute or relative to the working folder. Default filename is "user-sync-config.yml" |
| `--users` `all`<br />`--users` `file` _input_path_<br />`--users` `group` _grp1,grp2_<br />`--users` `mapped` | Specify the users to be selected for sync. The default is `all` meaning all users found in the directory. Specifying `file` means to take input user specifications from the CSV file named by the argument. Specifying `group` interprets the argument as a comma-separated list of groups in the enterprise directory, and only users in those groups are selected. Specifying `mapped` is the same as specifying `group` with all groups listed in the group mapping in the configuration file. This is a very common case where just the users in mapped groups are to be synced.|
| `--user-filter` _regex\_pattern_ | Limit the set of users that are examined for syncing to those matching a pattern specified with a regular expression. See the [Python regular expression documentation](https://docs.python.org/2/library/re.html) for information on constructing regular expressions in Python. The user name must completely match the regular expression.|
| `--update-user-info` | When supplied, synchronizes user information. If the information differs between the enterprise directory side and the Adobe side, the Adobe side is updated to match. This includes the firstname and lastname fields. |
| `--process-groups` | When supplied, synchronizes group membership information. If the membership in mapped groups differs between the enterprise directory side and the Adobe side, the group membership is updated on the Adobe side to match. This includes removal of group membership for Adobe users not listed in the directory side (unless the `--adobe-only-user-action exclude` option is also selected).|
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;filename<br/><br/>`--adobe-only-user-action  exclude` | When supplied, if user accounts are found on the Adobe side that are not in the directory, take the indicated action.  <br/><br/>`preserve`: no action concerning account deletion is taken. This is the default.  There may still be group membership changes if the `--process-groups` option was specified.<br/><br/>`remove-adobe-groups`: The account is removed from user groups and product configurations, freeing any licenses it held, but is left as an active account in the organization.<br><br/>`remove`: In addition to remove-adobe-groups, the account is also removed from the organization, but the user account, with its associated assets, is left in the domain and can be re-added to the organization if desired.<br/><br/>`delete`: In addition to the action for remove, the account is deleted if its domain is owned by the organization.<br/><br/>`write-file`: No action concerning account deletion is taken. The list of user accounts present on the Adobe side but not in the directory is written to the file indicated.  You can then pass this file to the `--adobe-only-user-list` argument in a subsequent run.  There may still be group membership changes if the `--process-groups` option was specified.<br/><br/>`exclude`: No update of any kind is applied to users found only on the Adobe side.  This is used when doing updates of specific users via a file (`--users file f`) where only users needing explicit updates are listed in the file and all other users should be left alone.<br/><br>Only permitted actions will be applied.  Accounts of type adobeID are owned by the user so the delete action will do the equivalent of remove.  The same is true of Adobe accounts owned by other organizations. |
| `--adobe-only-user-list` _filename_ | Specifies a file from which a list of users will be read.  This list is used as the definitive list of "Adobe only" user accounts to be acted upon.  One of the `--adobe-only-user-action` directives must also be specified and its action will be applied to user accounts in the list.  The `--users` option is disallowed if this option is present: only account removal actions can be processed.  |
| `--config-file-encoding` _encoding_name_ | Optional.  Specifies the character encoding for the contents of the configuration files themselves.  This includes the main configuration file, "user-sync-config.yml" as well as other configuration files it may reference.  Default is `utf8` for User Sync 2.2 and later and `ascii` for earlier versions.<br />Character encoding in the user source data (whether csv or ldap) is declared by the connector configurations, and that encoding can be different than the encoding used for the configuration files (e.g., you could have a latin-1 configuration file but a CSV source file that uses utf-8 encoding).<br />The available encodings are dependent on the Python version used; see the documentation [here](https://docs.python.org/2.7/library/codecs.html#standard-encodings) for more information.  |
| `--strategy sync`<br />`--strategy push` | Available in release 2.2 and later. Optional.  Default operating mode is `--strategy sync`.   Controls whether User Sync reads user information from Adobe and compares to the directory information and then issues updates to Adobe, or simply pushes the directory input to Adobe without considering the existing user information on Adobe.  `sync` is the default and the subject of the description of most of this documentation.  `push` is useful when there is a large number of users on the Adobe side (>30,000) and known additions or changes to a small number of users are desired, and the list of those users is available in a csv file or a specific directory group.<br />If `--strategy push` is specified, `--adobe-only-user-action` cannot be specified as the determination of adobe-only users is not made.<br/>`--strategy push` will create new users, modify their group memberships for mapped groups only (if `--process-groups` is present),  update user information (if `--update-user-info` is present), and will not remove users from the organization or delete their accounts.  See [Handling Push Notifications](usage_scenarios.md#handling-push-notifications) for information on how to remove users via push notifications. |
| `--connector ldap`<br />`--connector okta`<br />`--connector csv` _filename_ | Available in release 2.3 and later. Optional. Specifies the directory connector to be used (defaults to LDAP).  If you specify the use of a CSV input file with this argument, then you cannot also specify one with `--users`, but you can then specify other `--users` options (such as `mapped` or `group`) for use with the CSV file.  (The Okta connector does not support `--users all`, so you must specify a `--users` option of `mapped` or `group` if you use the Okta connector.)
{: .bordertablestyle }

---

[Previous Section](configuring_user_sync_tool.md)  \| [Next Section](usage_scenarios.md)
