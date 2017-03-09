## Choose Final Command Line Options

[Previous Section](monitoring.md) | [Back to Contents](Contents.md) |  [Next Section](scheduling.md)

The command line for user sync selects the set of users to be processed, specifies whether user group and PC membership should be managed, specifies how account deletion should be handled, and a few additional options.

### Users


| Users Command line option  | Use when           |
| ------------- |:-------------| 
|   `--users all` |    All users listed in the directory are included.  |
|   `--users group "g1,g2,g3"`  |    The named directory groups are used to form the user selection. <br>Users that are members of any of the groups are included.  |
|   `--users file f`  |    The file f is read to form the selected set of users.  The LDAP directory is not used in this case. |
|   `--user-filter pattern`    |  Can be combined with the above options to further filter and reduce the user selection. <br>`pattern` is a string in Python regular expression format.  <br>The user name must match the pattern in order to be included.  <br>Writing patterns can be somewhat of an art.  See examples below or refer to the Python documentation [here](https://docs.python.org/2/library/re.html). |


If all users listed in the directory are to be synced to Adobe, use `--users all`.  If only some users, you can limit the set by altering the LDAP query in the `connector-ldap.yml` configuration file (and use `--users all`), or you can limit the users to those in specific groups (by using --users group).  You can combine either of these with a `--user-filter pattern` to further limit the selected set of users to be synced.

If you are not using a directory system, you can use `--users file f` to select users from a csv file.  See the example users file (`csv inputs - user and remove lists/1 users-file.csv`) to see the format.  Groups listed in the csv files are names you can choose.  They are mapped to Adobe user groups or PCs in the same manner as with directory groups.

### Groups

If you are not managing product licenses with sync, you do not need to specify the group map in the configuration file and do not need to add any command line parameters for group processing.

If you are managing licenses with user sync, include the option `--process-groups` on the command line.


### Account Deletion


There are several command line options that allow you to specify the action to be taken when an Adobe account with no corresponding directory account is found (a “nonexistent” user).
Note that only the users returned by the directory query and filter are considered as "existing".



| Command line option       ...........| Use when           |
| ------------- |:-------------| 
|   None                        |  No action desired on nonexistent users |
|   `--disable-nonexistent-users`\* |    Adobe account to remain but licenses and group <br>memberships are removed.  |
|   `--remove-nonexistent-users`  |    Adobe account to remain but licenses, group memberships, and membership in this org to be removed   |
|   `--delete-nonexistent-users`\*  |    Adobe account to be deleted: remove from PLCs and user groups and <br>from the org; account deleted and all storage and settings freed. |
|   `--generate-remove-list f`    |  No action to be taken on the account.  User name written to file for later action. |

\* These options will be available in a future release.

### Other Options

`--test-mode`:  causes User Sync to run through all processing including querying the directory and calling the Adobe User Management APIs to process the request, but no actual action is taken.  No users are created, deleted, or altered.

`--update-user-info`: causes User Sync to check for changes in first name, last name, or email address of users and make updates to the Adobe information if it does not match the directory information.  Specifying this option increases run time so you may not want to include it on each run.


### Examples

A few examples:

`user-sync --users all --process-groups --remove-nonexistent-users`

- Process all users based on config settings, update Adobe group membership, and if there are any users listed in the org that are not in the directory, remove them.
    
`user-sync --users file example.users-file.csv --process-groups --remove-nonexistent-users`

- The file “example.users-file.csv” is read as the master user list. No attempt is made to contact a directory service such as AD or LDAP in this case.

### Define your command line

You may want to make your first few runs without any deletion options.

&#9744;  Put together the command line options you need for your run of user sync.


[Previous Section](monitoring.md) | [Back to Contents](Contents.md) |  [Next Section](scheduling.md)
