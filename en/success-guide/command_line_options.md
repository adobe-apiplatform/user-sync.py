---
layout: default
lang: en
nav_link: Command Line
nav_level: 2
nav_order: 310
parent: success-guide
page_id: command-line-options
---

# Choose Final Command Line Options

[Previous Section](monitoring.md) \| [Back to Contents](index.md) \|  [Next Section](scheduling.md)

The command line for user sync selects the set of users to be processed, specifies whether user group and PC membership should be managed, specifies how account deletion should be handled, and a few additional options.

## Users


| Users Command line option  | Use when           |
| ------------- |:-------------| 
|   `--users all` |    All users listed in the directory are included.  |
|   `--users group "g1,g2,g3"`  |    The named directory groups are used to form the user selection. <br>Users that are members of any of the groups are included.  |
|   `--users mapped`  |    The same as `--users group g1,g2,g3,...`, where `g1,g2,g3,...` are all the directory groups specified in the configuration file group mapping.|
|   `--users file f`  |    The file f is read to form the selected set of users.  The LDAP directory is not used in this case. |
|   `--user-filter pattern`    |  Can be combined with the above options to further filter and reduce the user selection. <br>`pattern` is a string in Python regular expression format.  <br>The user name must match the pattern in order to be included.  See examples below or refer to the [Python documentation](https://docs.python.org/3/library/re.html). |
{: .bordertablestyle }


If all users listed in the directory are to be synced to Adobe, use `--users all`.  If only some users, you can limit the set by altering the LDAP query in the `connector-ldap.yml` configuration file (and use `--users all`), or you can limit the users to those in specific groups (by using --users group).  You can combine either of these with a `--user-filter pattern` to further limit the selected set of users to be synced.

If you are not using a directory system, you can use `--users file f` to select users from a csv file.  See the example users file (`csv inputs - user and remove lists/users-file.csv`) to see the format.  Groups listed in the csv files are names you can choose.  They are mapped to Adobe user groups or PCs in the same manner as with directory groups.

## Groups

If you are not managing product licenses with sync, you do not need to specify the group map in the configuration file and do not need to add any command line parameters for group processing.

If you are managing licenses with user sync, include the option `--process-groups` on the command line.


## Account Deletion


There are several command line options that allow you to specify the action to be taken when an Adobe account with no corresponding directory account is found (an “Adobe only” user).
Note that only the users returned by the directory query and filter are considered as "existing" in the enterprise directory.  These options range from "completely ignore" to "completely delete" with several possibilities in between.



| Command line option       ...........| Use when           |
| ------------- |:-------------| 
|   `--adobe-only-user-action exclude`                        |  No action desired on accounts that exist only in Adobe and have no corresponding directory account. Adobe group memberships are not updated even if `--process-groups` is present. |
|   `--adobe-only-user-action preserve`                        |  No removal or deletion of accounts that exist only in Adobe and have no corresponding directory account. Adobe group memberships are updated if `--process-groups` is present. |
|   `--adobe-only-user-action remove-adobe-groups` |    Adobe account to remain but licenses and group <br>memberships are removed.  |
|   `--adobe-only-user-action remove`  |    Adobe account to remain but licenses, group memberships, and listing in the Adobe Admin console are removed   |
|   `--adobe-only-user-action delete`  |    Adobe account to be deleted: remove from<br>Adobe product configurations and user groups; account deleted and all storage and settings freed. |
|   `--adobe-only-user-action write-file f.csv`    |  No action to be taken on the account.  User name written to file for later action. |
{: .bordertablestyle }



## Other Options

`--test-mode`:  causes User Sync to run through all processing including querying the directory and calling the Adobe User Management APIs to process the request, but no actual action is taken.  No users are created, deleted, or altered.

`--update-user-info`: causes User Sync to check for changes in first name, last name, or email address of users and make updates to the Adobe information if it does not match the directory information.  Specifying this option may increase run time.


## Examples

A few examples:

`user-sync --users all --process-groups --adobe-only-user-action remove`

- Process all users based on config settings, update Adobe group membership, and if there are any Adobe users that are not in the directory, remove them from the Adobe side, freeing any licenses they may have been allocated.  The Adobe account is not deleted so that it can be re-added and/or stored assets recovered.
    
`user-sync --users file users-file.csv --process-groups --adobe-only-user-action remove`

- The file “users-file.csv” is read as the master user list. No attempt is made to contact a directory service such as AD or LDAP in this case.  Adobe group membership is updated per the information in the file, and any Adobe accounts not listed in the file are removed (see definition of remove, above).

## Define your command line

You may want to make your first few runs without any deletion options.

&#9744;  Put together the command line options you need for your run of user sync.


[Previous Section](monitoring.md) \| [Back to Contents](index.md) \|  [Next Section](scheduling.md)
