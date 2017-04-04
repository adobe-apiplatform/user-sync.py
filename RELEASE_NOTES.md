# Release Notes for User Sync Tool Version 1.2

These notes apply to 2.0rc1 of 2017-04-03.

## New Arguments & Configuration Syntax

There has been an extensive overhaul of both the configuration file
syntax and the command-line argument syntax.  See
[Issue 95](https://github.com/adobe-apiplatform/user-sync.py/issues/95)
and the [docs](https://adobe-apiplatform.github.io/user-sync.py/)
for details.

## New Features

1. You can now exclude dashboard users from being updated or
deleted by User Sync. See the
[docs](https://adobe-apiplatform.github.io/user-sync.py/) for
details.
2. There is more robust reporting for errors in configuration
files.
3. The log now reports the User Sync version and gives the
details of how it was invoked.
4. You can now create and manage users of all identity types,
including Adobe IDs, both when operating from an LDAP
directory and from CSV files.
5. You can now distinguish, when a customer directory user is
disabled or removed, whether to remove the matching Adobe-side
user's product configurations and user groups, to remove the
user but leave his cloud storage, or to delete his storage as well.
   
## Significant Bug Fixes

1. There were many bugs fixed related to managing users of
identity types other than Federated ID.
2. There were many bugs fixes related to managing group
membership of all identity types.
3. There was a complete overhaul of how users who have
adobe group memberships in multiple organizations are
managed.

## Changes in Behavior

All options now apply to users of all identity types. Previously,
some had applied only to Federated ID and some to Enterprise ID.

## Compatibility with Prior Versions

All existing configuration files, user input files,
and command-line scripts will need to be revamped
to be compatible with the new formats.  Here is a quick
cheat sheet of what needs to be done:

* replace `dashboard:` with `adobe_users:`
* replace `directory:` with `directory_users:`
* add a `connectors:` section under `adobe_users:` similar
to the one under `directory_users`
* change `owning` to be `umapi` and put it under `connectors`
* if you access multiple organizations, remove
`secondaries`, and put
all the umapi specifications under `umapi` as a list,
like this:
```yaml
adobe_users:
  connectors:
    umapi:
      - primary-config.yml
      - org1: org1-config.yml
      - org2: org2-config.yml
```
* change `dashboard_groups` to `adobe_groups`
* under `limits`, change `max_missing_users` to
`max_adobe_only_users` and remove all other
settings
* if you have an extension, do the following:
  * remove the per-context: user setting
  * move all the settings under it to the top level in
a new file, call it `extension.yaml`
  * change `extensions` to `extension`, move it into
the `directory_users` section, and put the relative
path to the new `extension.yaml` file as its value.



