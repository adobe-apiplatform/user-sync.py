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
| `-t`<br />`--test-mode`<br />`-T`<br />`--no-test-mode` | Specifying `-t` or `--test-mode` causes User Sync to run API action calls in _test mode_ (that is, the server does syntax/semantics checking on the calls but does not execute any requested changes). User Sync still logs all actions, making this very useful for previewing what a run would have requested. Starting with version 2.3, specifying `-T` or `--no-test-mode` can be specified to turn off test mode, which is useful to override a default value specified in the configuration file (see below). |
| `-c` _filename_<br />`--config-filename` _filename_ | The complete path to the main configuration file, absolute or relative to the working folder. Default filename is "user-sync-config.yml" |
| `--users` `all`<br />`--users` `file` _input_path_<br />`--users` `group` _grp1,grp2_<br />`--users` `mapped` | Specify the users to be selected for sync. The default is `all` meaning all users found in the directory. Specifying `file` means to take input user specifications from the CSV file named by the argument. Specifying `group` interprets the argument as a comma-separated list of groups in the enterprise directory, and only users in those groups are selected. Specifying `mapped` is the same as specifying `group` with all groups listed in the group mapping in the configuration file. This is a very common case where just the users in mapped groups are to be synced.|
| `--user-filter` _regex\_pattern_ | Limit the set of users that are examined for syncing to those matching a pattern specified with a regular expression. See the [Python regular expression documentation](https://docs.python.org/2/library/re.html) or [for Python 3](https://docs.python.org/3/library/re.html) for information on constructing regular expressions in Python. The user name must completely match the regular expression.|
| `--update-user-info`<br />`--no-update-user-info` | Specifying `--update-user-info` synchronizes user information. If the information differs between the enterprise directory side and the Adobe side, the Adobe side is updated to match. This includes the firstname and lastname fields.  Starting with User Sync 2.3, `--no-update-user-info` can be specified to prevent this synchronization, which is useful to override a default value specified in the configuration file (see below). |
| `--process-groups`<br />`--no-process-groups` | Specifying `--process-groups` causes synchronization of group membership information: if the membership in mapped groups differs between the enterprise directory side and the Adobe side, the group membership is updated on the Adobe side to match. This includes removal of group membership for Adobe users not listed in the directory side (unless the `--adobe-only-user-action exclude` option is also selected).  Starting with User Sync 2.3, `--no-process-groups` can be specified to prevent this synchronization, which is useful to override a default value specified in the configuration file (see below). |
| `--adobe-only-user-action preserve`<br />`--adobe-only-user-action remove-adobe-groups`<br />`--adobe-only-user-action  remove`<br />`--adobe-only-user-action delete`<br /><br/>`--adobe-only-user-action  write-file`&nbsp;filename<br/><br/>`--adobe-only-user-action  exclude` | When supplied, if user accounts are found on the Adobe side that are not in the directory, take the indicated action.  <br/><br/>`preserve`: no action concerning account deletion is taken. This is the default.  There may still be group membership changes if the `--process-groups` option was specified.<br/><br/>`remove-adobe-groups`: The account is removed from user groups and product configurations, freeing any licenses it held, but is left as an active account in the organization.<br><br/>`remove`: In addition to remove-adobe-groups, the account is also removed from the organization, but the user account, with its associated assets, is left in the domain and can be re-added to the organization if desired.<br/><br/>`delete`: In addition to the action for remove, the account is deleted if its domain is owned by the organization.<br/><br/>`write-file`: No action concerning account deletion is taken. The list of user accounts present on the Adobe side but not in the directory is written to the file indicated.  You can then pass this file to the `--adobe-only-user-list` argument in a subsequent run.  There may still be group membership changes if the `--process-groups` option was specified.<br/><br/>`exclude`: No update of any kind is applied to users found only on the Adobe side.  This is used when doing updates of specific users via a file (`--users file f`) where only users needing explicit updates are listed in the file and all other users should be left alone.<br/><br>Only permitted actions will be applied.  Accounts of type adobeID are owned by the user so the delete action will do the equivalent of remove.  The same is true of Adobe accounts owned by other organizations. |
| `--adobe-only-user-list` _filename_ | Specifies a file from which a list of users will be read.  This list is used as the definitive list of "Adobe only" user accounts to be acted upon.  One of the `--adobe-only-user-action` directives must also be specified and its action will be applied to user accounts in the list.  The `--users` option is disallowed if this option is present: only account removal actions can be processed.  |
| `--config-file-encoding` _encoding_name_ | Optional.  Specifies the character encoding for the contents of the configuration files themselves.  This includes the main configuration file, "user-sync-config.yml" as well as other configuration files it may reference.  Default is `utf8` for User Sync 2.2 and later and `ascii` for earlier versions.<br />Character encoding in the user source data (whether csv or ldap) is declared by the connector configurations, and that encoding can be different than the encoding used for the configuration files (e.g., you could have a latin-1 configuration file but a CSV source file that uses utf-8 encoding).<br />The available encodings are dependent on the Python version used; see the documentation [here for Python 2.7](https://docs.python.org/2.7/library/codecs.html#standard-encodings) or [here for Python 3.6](https://docs.python.org/3.6/library/codecs.html#standard-encodings) for more information.  |
| `--strategy sync`<br />`--strategy push` | Available in release 2.2 and later. Optional.  Default operating mode is `--strategy sync`.   Controls whether User Sync reads user information from Adobe and compares to the directory information and then issues updates to Adobe, or simply pushes the directory input to Adobe without considering the existing user information on Adobe.  `sync` is the default and the subject of the description of most of this documentation.  `push` is useful when there is a large number of users on the Adobe side (>30,000) and known additions or changes to a small number of users are desired, and the list of those users is available in a csv file or a specific directory group.<br />If `--strategy push` is specified, `--adobe-only-user-action` cannot be specified as the determination of adobe-only users is not made.<br/>`--strategy push` will create new users, modify their group memberships for mapped groups only (if `--process-groups` is present),  update user information (if `--update-user-info` is present), and will not remove users from the organization or delete their accounts.  See [Handling Push Notifications](usage_scenarios.md#handling-push-notifications) for information on how to remove users via push notifications. |
| `--connector ldap`<br />`--connector okta`<br />`--connector csv` _filename_ | Available in release 2.3 and later. Optional. Specifies the directory connector to be used (defaults to LDAP).  If you specify the use of a CSV input file with this argument, then you cannot also specify one with `--users`, but you can then specify other `--users` options (such as `mapped` or `group`) for use with the CSV file.  (The Okta connector does not support `--users all`, so you must specify a `--users` option of `mapped` or `group` if you use the Okta connector.) |
| `--adobe-users all`<br />`--adobe-users mapped`<br />`--adobe-users group` _grp1,grp2_ | Available in release 2.4 and later. Optional. Specify the adobe users to be selected for sync. The default is all meaning all users found in Adobe Admin Console. Specifying group interprets the argument as a comma-separated list of groups (product profile or user-group) in the console, and only users in those groups are selected. Specifying mapped is the same as specifying group with all the adobe groups listed in the group mapping in the configuration file.
{: .bordertablestyle }

As of version 2.3 of User Sync, the values of most command-line parameters can also be specified in the main configuration file, in an optional section called `invocation_defaults`.  Here is an example use of that section:

```yaml
invocation_defaults:
  adobe_only_user_action:
    - write-file
    - adobe-only-users.csv
  connector: [csv, users-file.csv]
  process_groups: Yes
  strategy: sync
  test_mode: Yes
  update_user_info: True
  users: mapped
```

As you can see from the example:

* Each command-line parameter can be specified using a configuration option whose name is the same, but with hyphens replaced by underscores; for example, the command-line parameter `process-groups` is specified by the configuration option `process_groups`. (YAML doesn't allow hyphens in option names.)  Only those command-line parameters which control the loading of configuration files (`--config-filename`, `--config-file-encoding`) cannot be specified as configuration options, because they take effect _before_ the configuration file is loaded.
* Command-line parameters that take zero arguments because they specify Yes/No (boolean) options (`--test-mode`, `--process-groups`, `--update-user-info`) can be specified as having a value of Yes/True or No/False (case-insensitive), since YAML syntax treats these all as booleans.  The example above contains configuration options that use both formats.
* Command-line parameters that are being given a single string argument should have the desired string specified as their value, as shown for the `users` option above.
* Command-line parameters that are being given multiple string arguments should have a list of the desired strings specified as their value.  YAML supports two options for specifying lists of values, one of which (single-line) is shown for the `connector` option above and the other of which (multi-line) is shown for the `adobe_only_user_action` above.  (A list containing a single string is treated the same as a single string argument.)

The handling of parameter values is identical regardless of whether the value is specified in the configuration file or on the command line.  So, for example, specifying a filename on the command line interprets that filename relative to the User Sync working directory, and the same applies to filenames specified in the `invocation_defaults` section of the configuration file.

Command-line parameters that are actually specified on the command line take precedence over any specified in the configuration file.  To be precise, if a value is specified for a parameter on the command line, any value specified in the configuration file will be ignored.

---

[Previous Section](configuring_user_sync_tool.md)  \| [Next Section](usage_scenarios.md)
