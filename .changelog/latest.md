# New Features

This is the first release candidate for the **Users In Multiple Groups** (UMG) feature. This feature allows Sign Sync to target Sign accounts with UMG enabled to fully utilize the User Sync Tool.

UMG sync can be enabled in the `user_sync` config setting:

```yaml
user_sync:
  sign_only_limit: 100
  sign_only_user_action: reset
  # default is False
  umg: True
```

With UMG enabled, the `sign_group` setting in a group mapping can be a list of Sign groups to target:

```yaml
- directory_group: Sign Users
  sign_group:
    - Group 1
    - Group 2
```

Group admin status is assigned differently. If `group_admin` is set to `True`, then groups for the user to admin must be specified in their own list.

```yaml
- directory_group: Sign Users
  sign_group:
    - Group 1
    - Group 2
  # groups specified in "group_admin" list must be present in
  # sign_group list
  group_admin: True
  admin_groups:
    - Group 1
```

(note: `group_admin` is actually deprecated and can be omitted. `admin_groups` is sufficient for managing group admin status)

Account admin status is also handled differently in this release. The `account_admin` field inside a group mapping rule is still permitted for now, but is deprecated. Instead, directory groups that grant account admin status should be set using `account_admin_groups`.

```yaml
account_admin_groups:
  - Sign Admins 1
  - Sign Admins 2
```

Finally, since a user's primary group impacts several key aspects of user experience, if UMG is enabled, then rules must be specified to designate primary groups for all users. `primary_group_rules` is a new config construct that specifies rules to designate a primary group given different sets of Sign groups.

**NOTE:** Primary group rules are evaluated after group management rules are resolved. `sign_groups` may contain groups that aren't specified in group mappings.

```yaml
primary_group_rules:
  # sign_groups list can specify groups that aren't necessarily assigned
  # the user in the sync tool
  - sign_groups:
      - Sign Group 1
      - Sign Group 2
    # assign the primary group only if the user is a member of all groups
    # specified in sign_groups
    primary_group: Sign Group 2
```

# Notes

* **Sign Sync:** Cache funtionality is disabled for the time being
