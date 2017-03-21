# Release Notes for User Sync Tool Version 1.2

These notes apply to 1.2rc1 of 2017-03-20.z

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
   from the organization or also to delete his Adobe user
   account.
   
## Significant Bug Fixes

1. There were many bugs fixed related to managing users of
   identity types other than Federated ID.
2. There were many bugs fixes related to managing group
   membership of all identity types.

## Changes in Behavior

All options now apply to users of all identity types. Previously,
some had applied only to Federated ID and some to Enterprise ID.

## Compatibility with Prior Versions

Other than as noted above, existing configuration files and
should work and have the same behavior.
