---
layout: default
lang: en
nav_link: Configure User Sync
nav_level: 2
nav_order: 30
---

[Previous Section](setup_and_installation.md)  \| [Next Section](connect_adobe.md)

# Configuring the User Sync Tool
{:."no_toc"}

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

## Overview

User Sync Tool behavior is governed by a set of configuration files.

These files are typically placed in the same directory as the User Sync Tool executable.

While this overview covers the configuration files for Sign Sync, this section focuses on UMAPI sync. See
[Sign Sync](sign_sync.md) for details around configuring Sign Sync.

### Core Configuration (Admin Console)

These configuration files are required to synchronize users to the Admin Console.

* `user-sync-config.yml` - Main config file for Admin Console Sync
* `connector-umapi.yml` - Defines connection to the [User Management API](https://adobe-apiplatform.github.io/umapi-documentation/en/). Stores
credentials (or keychain references) and defines advanced connection options. If you plan to synchronize to multiple UMAPI targets, then each
connection is configured in a different UMAPI connector config file.

### Core Configuration (Sign Sync)

These configuration files are required to synchronize users to Adobe Acrobat Sign.

* `sign-sync-config.yml` - Main config file for Sign Sync
* `connector-sign.yml` - Defines a connection to a Sign account (using the [Sign API](https://helpx.adobe.com/sign/faq/api.html)).
Multiple connections are supported (each in their own connector config file).

### Directory Connector Configuration

These configuration files define connections to various identity sources. They can be used with both UMAPI sync and Sign Sync.
They are only required if the connector is enabled (TODO see below). The exception - when using UMAPI sync, `connector-csv.yml`
is totally optional assuming the CSV uses the standard headers and encoding (`utf-8`). The CSV connector is required when using
Sign Sync.

* `connector-ldap.yml` - Defines connection to an LDAP system such as Active Directory
* `connector-okta.yml` - Defines connection to an Okta tenant (using the Okta API)
* `connector-adobe-console.yml` - Defines a connection to the UMAPI for treating an Admin Console organization as an identity source. Useful
in cases when synchronizing to a console-linked Sign account, or when syncing to an Admin Console org with a trusted Azure AD-synced directory
* `connector-csv.yml` - Defines header columns and encoding of CSV input file

### Advanced Configuration

The extension config (`extension-config.yml`) can be set up for use with UMAPI sync to get more control over how syncs are
executed. See [advanced configuration](advanced_configuration.md#custom-attributes-and-mappings) for details.

## Config File Setup

Example configuration files can be obtained in several ways:

* In the `examples` folder of the [code repository](https://github.com/adobe-apiplatform/user-sync.py/tree/v2/examples)
* The example bundles (`user-sync-examples.zip` or `user-sync-examples.tar.gz`) on
[any release page](https://github.com/adobe-apiplatform/user-sync.py/releases/latest)
* Running `./user-sync init` or `./user-sync example-config` from the command line (**recommended**)

Configurations files are in [YAML format](http://yaml.org/)
and use the `yml` suffix. When editing YAML, remember some
important rules:

* Indentation governs scope and heirarchy (as opposed to a system like JSON which uses curly braces)

* Keys and values are delimited with a single colon (`:`) followed by a space character

  ```yml
  some_key: A Value
  ```

* A dash (`-`) denotes a list item

  ```yml
  # example with one item
  adobe_groups:
	- Photoshop Users

  # example with multiple items
  adobe_groups:
    - Photoshop Users
    - Lightroom Users
    - Illustrator Users
  ```

**Tip:** use a developer-friendly text editor such as [Notepad++](https://notepad-plus-plus.org/) for maximum ease-of-use.

If you're not using Windows, we recommend an editor with these features.

* Line numbers
* YAML syntax highlighting
* Smart indentation
* Ability to set line endings and file encoding
* Ability to show special characters (tabs, line endings, etc)

## Configuring Identity Sources

### Admin Console Connector

### CSV Connector

## Configuration options

The main configuration file, user-sync-config.yml, is divided
into several main sections: **adobe_users**, **directory_users**,
**limits**, and **logging**.

- The **adobe_users** section specifies how the User Sync tool
connects to the Adobe Admin Console through the User Management
API. It should point to the separate, secure configuration file
that stores the access credentials.  This is set in the umapi field of
the connectors field.
    - The adobe_users section also can contain exclude_identity_types,
exclude_adobe_groups, and exclude_users which limit the scope of users
affected by User Sync.  See the later section
[Protecting Specific Accounts from User Sync Deletion](advanced_configuration.md#protecting-specific-accounts-from-user-sync-deletion)
which describes this more fully.
- The **directory_users** subsection contains two subsections,
connectors and groups:
    - The **connectors** subsection points to the separate,
secure configuration file that stores the access credentials for
your enterprise directory.
    - The **groups** section defines the mapping between your
directory groups and Adobe product configurations and user
groups.
    - **directory_users** can also contain keys that set the default country
code and identity type.  See the example configuration files for details.
- The **limits** section sets the `max_adobe_only_users` value that
prevents User Sync from updating or deleting Adobe user accounts if
there are more than the specified value of accounts that appear in
the Adobe organization but not in the directory. This
limit prevents removal of a large number of accounts
in case of misconfiguration or other errors.  This is a required item.
- The **logging** section specifies an audit trail path and
controls how much information is written to the log.

### Configure connection files

The main User Sync configuration file contains only the names of
the connection configuration files that actually contain the
connection credentials. This isolates the sensitive information,
allowing you to secure the files and limit access to them.

Provide pointers to the connection configuration files in the
**adobe_users** and **directory_users** sections:

```
adobe_users:
  connectors:
    umapi: connector-umapi.yml

directory_users:
  connectors:
    ldap: connector-ldap.yml
```

### Configure group mapping

Before you can synchronize user groups and entitlements, you must
create user groups and product configurations in the
Adobe Admin Console, and corresponding groups in your enterprise
directory, as described above in
[Set up product-access synchronization](setup_and_installation.md#set-up-product-access-synchronization).

**NOTE:** All groups must exist and have the specified names on
both sides. User Sync does not create any groups on either side;
if a named group is not found, User Sync logs an error.

The **groups** section under **directory_users** must have an entry for
each enterprise directory group that represents access to an
Adobe product or products. For each group entry, list the product
configurations to which users in that group are granted
access. For example:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - "Default Acrobat Pro DC configuration"
  - directory_group: Photoshop
    adobe_groups:
      - "Default Photoshop CC - 100 GB configuration"
      - "Default All Apps plan - 100 GB configuration"
```

Directory groups can be mapped to either *product configurations*
or *user groups*. An `adobe_groups` entry can name either kind
of group.

For example:

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - Default Acrobat Pro DC configuration
  - directory_group: Acrobat_Accounting
    adobe_groups:
      - Accounting_Department
```

### Mapping Admin Roles

Admin roles can be assigned to users by the User Sync tool using
special group names and prefixes.  Using these special naming
conventions, admin roles can be assigned like any normal product
profile or user group.

| Admin Role | Name or Prefix |
|:---|:---|
| System Admin* | `_org_admin` |
| Support Admin | `_support_admin` |
| Deployment Admin | `_deployment_admin` |
| User Group or Profile Admin | `_admin_[GROUP_NAME]` |
| Product Admin | `_product_admin_[PRODUCT_NAME]` |
{: .bordertablestyle }

*System admin roles can't currently be assigned by the UMAPI, so they
are not supported in the User Sync Tool

**Notes about the Product Admin role:**

* It may be necessary to manually assign a user as admin to a product
before syncing users as product admins.
* The product admin role group name is case-sensitive.
* It is often necessary to assign users to at least one profile on the
same product as the admin role.

See the [UMAPI Docs](https://adobe-apiplatform.github.io/umapi-documentation/en/api/ActionsCmds.html#addRemoveAttr) for more details.

#### Role Assignment Example

```YAML
groups:
  - directory_group: Acrobat Admins
    adobe_groups:
      # assuming the product name is "Adobe Acrobat Pro DC"
      - Default Acrobat Pro DC configuration
      - _product_admin_Adobe Acrobat Pro DC
  - directory_group: Support and Deployment Admins
    adobe_groups:
      - _support_admin
      - _deployment_admin
  - directory_group: Department A Admins
    adobe_groups:
      # assuming a user group called "Department A"
      - Department A
      - _admin_Department A
```


### Configure limits

User accounts are removed from the Adobe system when
corresponding users are not present in the directory and the tool
is invoked with one of the options

- `--adobe-only-user-action delete`
- `--adobe-only-user-action remove`
- `--adobe-only-user-action remove-adobe-groups`

If your organization has a large number of users in the
enterprise directory and the number of users read during a sync
is suddenly small, this could indicate a misconfiguration or
error situation.  The value of `max_adobe_only_users` is a threshold
which causes User Sync to suspend deletion and update of existing Adobe accounts
and report an error if there are
this many fewer users in the enterprise directory (as filtered by query parameters) than in the
Adobe admin console.

Raise this value if you expect the number of users to drop by
more than the current value.

Example 1:

```YAML
limits:
  max_adobe_only_users: 200
```

This configuration causes User Sync to check if more than
200 user accounts present in Adobe are not found in the enterprise directory (as filtered),
and if so no existing Adobe accounts are updated and an error message is logged.

Example 2:

```YAML
limits:
  max_adobe_only_users: 15%
```

This configuration causes User Sync to check if more than
15% user accounts present in Adobe are not found in the enterprise directory (as filtered),
and if so no existing Adobe accounts are updated and an error message is logged.

###  Configure logging

Log entries are written to the console from which the tool was
invoked, and optionally to a log file. A new
entry with a date-time stamp is written to the log each time User Sync
runs.

The **logging** section lets you enable and
disable logging to a file, and controls how much information is
written to the log and console output.

```YAML
logging:
  log_to_file: True | False
  file_log_directory: "path to log folder"
  file_log_name_format: "Python format string for datetime"
  file_log_level: debug | info | warning | error | critical
  console_log_level: debug | info | warning | error | critical
```

The log_to_file value turns file-logging on or off. Log messages are always
written to the console regardless of the log_to_file setting.

When file-logging is enabled, the file_log_directory value is
required. It specifies the folder where the log entries are to be
written.

- Provide an absolute path or a path relative to the folder
containing this configuration file.
- Ensure that the file and folder have appropriate read/write
permissions.

When file-logging is enabled, the file_log_name_format value is
an optional Python format string which takes as its only argument
the Python `datetime` value at the start of the run;
the format operation produces the name of the log file.  The default
value of this parameter, `{:%Y-%m-%d}.log`, produces a file
named for the date of the run in year-month-day format,
with the extension ".log", as `2017-11-21.log`.

Log-level values determine how much information is written to the
log file or console.

- The lowest level, debug, writes the most information, and the
highest level, critical, writes the least.
- You can define different log-level values for the file and
console.

Log entries that contain WARNING, ERROR or CRITICAL include a
description that accompanies the status. For example:

> `2017-01-19 12:54:04 7516 WARNING
console.trustee.org1.action - Error requestID: action_5 code:
"error.user.not_found" message: "No valid users were found in the
request"`

In this example, a warning was logged on 2017-01-19 at 12:54:04
during execution. An action caused an error with the code
“error.user.not_found”. The description associated with that
error code is included.

You can use the requestID value to search for the exact request
associated with a reported error. For the example, searching for
“action_5” returns the following detail:

> `2017-01-19 12:54:04 7516 INFO console.trustee.org1.action -
Added action: {"do":
\[{"add": {"product": \["default adobe enterprise support program configuration"\]}}\],
"requestID": "action_5", "user": "cceuser2@ensemble.ca"}`

This gives you more information about the action that resulted in
the warning message. In this case, User Sync attempted to add the
“default adobe enterprise support program configuration” to the
user "cceuser2@ensemble.ca". The add action failed because the
user was not found.

---

[Previous Section](setup_and_installation.md)  \| [Next Section](connect_adobe.md)
