# aedash-user-sync
User Sync for Adobe Enterprise Dashboard User Management

# Overview

The Adobe Enterprise Dashboard Connector automates user creation and product entitlement provisioning in the Enterprise Dashboard.  It takes a list of enterprise directory users, either from an LDAP connection, or from a tab-separated file, and creates, updates, or disables user accounts in the Dashboard.

# Requirements

* Python 2.7+
* User Management API Credentials (see [the official documentation](https://www.adobe.io/products/usermanagement/docs/gettingstarted))
* Accessible LDAP server (optional)

# Installation

The connector is packaged as a [self-contained .pex file](https://github.com/pantsbuild/pex).  See the releases page to get the latest build for your platform.

## Build Instructions

Requirements:

* Python 2.7+
* [virtualenv](https://virtualenv.pypa.io/en/stable/)
* If building on Debian - `python-dev libssl-dev libffi-dev libsasl2-dev libldap2-dev`
* GNU Make

To build, run `make pex` from the command line in the main repo directory.

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
  --users all|file|group [arg1 ...]
                        specify the users to be considered for sync. Legal
                        values are 'all' (the default), 'group name or names'
                        (one or more specified AD groups), 'file f' (a
                        specified input file).
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
                        Causes the user sync tool to remove Federated users
                        that exist on the Adobe side if they are not in the
                        customer side AD. This has the effect of deleting the
                        user account if that account is owned by the
                        organization under which the sync operation is being
                        run.
  --generate-remove-list output_path
                        processing similar to --remove-nonexistent-users
                        except that rather than performing removals, a file is
                        generated (with the given pathname) listing users who
                        would be removed. This file can then be given in the
                        --remove-list argument in a subsequent run.
  -d input_path, --remove-list input_path
                        specifies the file containing the list of users to be
                        removed. Users on this list are removeFromOrg'd on the
                        Adobe side.
```

# Configuration

See `examples/example.user-sync-config.yml` for the main configuration template.  The main configuation file user-sync-config.yml must exist in the configuration path.

See `examples/example.dashboard-config.yml` for the dashboard configuration template.  

See `examples/example.connector-ldap.yml` for the ldap configuration template.  

# Supported Workflows
