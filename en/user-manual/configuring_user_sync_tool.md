---
layout: default
lang: en
title: Configure User Sync
nav_link: Configure User Sync
nav_level: 2
nav_order: 30
parent: user-manual
page_id: configuration
---

[Previous Section](setup_and_installation.md)  \| [Next Section](connect_adobe.md)

# Configuring the User Sync Tool
{:."no_toc"}

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# Overview

User Sync Tool behavior is governed by a set of configuration files.

These files are typically placed in the same directory as the User Sync Tool executable.

Although this overview covers the configuration files for Sign Sync, this page focuses on UMAPI sync. See
[Sign Sync](sign_sync.md) for details around configuring Sign Sync.

After a brief overview of the configuration files used by the User Sync Tool and some general notes,
this page focuses on the configuration options used in `user-sync-config.yml`.

## Core Configuration (Admin Console)

These configuration files are required to synchronize users to the Admin Console.

* `user-sync-config.yml` - Main config file for Admin Console Sync
* `connector-umapi.yml` - Defines connection to the [User Management API](https://adobe-apiplatform.github.io/umapi-documentation/en/). Stores
credentials (or keychain references) and defines advanced connection options. If you plan to synchronize to multiple UMAPI targets, then each
connection is configured in a different UMAPI connector config file.

## Core Configuration (Sign Sync)

These configuration files are required to synchronize users to Adobe Acrobat Sign.

* `sign-sync-config.yml` - Main config file for Sign Sync
* `connector-sign.yml` - Defines a connection to a Sign account (using the [Sign API](https://helpx.adobe.com/sign/faq/api.html)).
Multiple connections are supported (each in their own connector config file).

## Directory Connector Configuration

These configuration files define connections to various identity sources. They
can be used with both UMAPI sync and Sign Sync. They are only required if the
connector is enabled. The exception - when using UMAPI sync, `connector-csv.yml`
is totally optional assuming the CSV uses the standard headers and encoding
(`utf-8`). The CSV connector is required when using Sign Sync.

* `connector-ldap.yml` - Defines connection to an LDAP system such as Active Directory
* `connector-okta.yml` - Defines connection to an Okta tenant (using the Okta API)
* `connector-adobe-console.yml` - Defines a connection to the UMAPI for treating an Admin Console organization as an identity source. Useful
in cases when synchronizing to a console-linked Sign account, or when syncing to an Admin Console org with a trusted Azure AD-synced directory
* `connector-csv.yml` - Defines header columns and encoding of CSV input file

## Advanced Configuration

The extension config (`extension-config.yml`) can be set up for use with UMAPI sync to get more control over how syncs are
executed. See [advanced configuration](advanced_configuration.md#custom-attributes-and-mappings) for details.

# Config File Setup

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

  ```yaml
  some_key: A Value
  ```

* A dash (`-`) denotes a list item

  ```yaml
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

# `user-sync-config.yml` Example

A basic example:

```yaml
adobe_users:
  exclude_identity_types:
  - adobeID
  exclude_adobe_groups:
  - _org_admin
  exclude_users:
  connectors:
    umapi: connector-umapi.yml

directory_users:
  default_country_code: US
  connectors:
    ldap: connector-ldap.yml
  user_identity_type: federatedID
  groups:
    - directory_group: adobe-all-apps
      adobe_groups:
        - All Apps
limits:
  max_adobe_only_users: 10%

logging:
  log_to_file: true
  file_log_directory: logs
  file_log_name_format: '{:%Y-%m-%d}.log'
  file_log_level: debug
  console_log_level: debug

invocation_defaults:
  adobe_only_user_action: preserve
  adobe_only_user_list:
  adobe_users: all
  connector: ldap
  process_groups: Yes
  strategy: sync
  test_mode: False
  update_user_info: True
  user_filter:
  users: mapped
```

# `adobe_users` Config

The `adobe_users` config key contains all of the options pertinent to Adobe-side sync management.

* Define Admin Console/User Management API (UMAPI) sync targets
* Define rules to exclude certain users from sync
  * Exclude certain identity types
  * Exclude certain groups
  * Exclude specific users by email address [regular expression](https://www.regular-expressions.info/)
  
Note that the exclusion rules defined here only apply to the Adobe-side workflow. That is to say these
filters are applied to user information queried from the Admin Console using the UMAPI.
  
## `exclude_identity_types`

This option defines a list of identity types to exclude. It generally should just be set to `adobeID` since it
isn't common for a console to have both `enterpriseID` directories and `federatedID` directories.

Example:

```yaml
  exclude_identity_types:
    - adobeID
```

`adobeID` users should generally always be excluded as a best practice.

## `exclude_adobe_groups`

Here the config defines a list of user groups or product profiles to exclude from sync. 

This can include any user group, product profile, or admin group you wish to exclude
from sync.

At minimum, it should include the special group name `_org_admin` which denotes
users with system admin privileges.

```yaml
  exclude_adobe_groups:
    - _org_admin
```

Note that you may have other users you might wish to exclude here - developer accounts, support admins, etc.
They should also be excluded here if needed.

## `exclude_users`

Exclude individual users by email address or a list of users with a [regular expression](https://www.regular-expressions.info/).

Example:

```yaml
  exclude_users:
    - "freelancer-[0-9]+.*"
```

## `connectors`

`adobe_users.connectors` defines one or more connections to the User Management API (UMAPI).

Each connection should at minimum contain a reference to the [UMAPI connector config](connect_adobe.md)
(e.g. `connector-umapi.yml`). Secondary targets also require an identifier field.

### Single Target

To configure a single target, `connectors` should be set to a single configuration file
reference. This should point to your main UMAPI config (e.g. `connector-umapi.yml`).

```yaml
adobe_users:
  connectors:
    umapi: connector-umapi.yml
```

The `umapi` key tells the sync tool that the UMAPI connector is in use.

### Multiple Targets

To target multiple console organizations, the `umapi` key is specified as a list instead of a
plain string.

Each target must have its own connector configuration file as well as its own set of UMAPI
credentials.

The User Sync Tool expects all target consoles to be related via
[directory trust](https://helpx.adobe.com/enterprise/using/directory-trust.html).

* The main target should own the directories and domains associated with UST-managed users
* Other targets should be trustees of the main target

This primary-secondary structure is represented in the `adobe_users.connectors` config:

```yaml
adobe_users:
  connectors:
    umapi:
      - connector-umapi.yml
      - org2: connector-umapi-org2.yml
```

Under the `umapi` key, the config file for the primary (identity-owning) target is
specified as a plain string. Each secondary target is specified as a key-value pair
with the key being a unique identifier for the target. This ID is used for several
key purposes:

* Targeting org-specific groups in the group mapping
* Distinguishing between targets in log messages
* Identifying different targets internally

## `update_attributes`

When `--update-user-info/update_user_info` is enabled (see [runtime
config](runtime_config.md)), the user attributes updated for a given user can be
controlled with `update_attributes`.

```yaml
adobe_users:
  #...
  update_attributes:
  # - username
  - firstname
  - lastname
  - email
```

By default, the `firstname`, `lastname` and `email` attributes are enabled for
updating. `username` is disabled by default.

If sync is run with `update_user_info` enabled and any changes are detected to a
disabled attribute for a given user, the Sync Tool logs a warning:

```
2023-07-12 13:32:55 54531 WARNING processor - 'username' has changed for user
 > 'federatedID,test.un.01@example.com,,test.user.01@example.com',
 > but that attribute isn't configured for updating
```

[line continuations added for clarity]

# `directory_users` Config

Every option under the `directory_users` key pertains to managing general identity
source behavior. This includes:

* Defining the connector type
* Linking the connector config file
* Defining default country code and identity type
* Defining how directory groups map to Adobe groups

## `default_country_code`

The country code is a mandatory attribute for every Adobe user. It governs the location
in which a user's data is stored, among other things.

When creating `federatedID` users, the country code must be specified on user creation.
On `enterpriseID` and `adobeID` users, it can be set to `UD` to leave the country undefined.
In this case, the user will select their own country when they log in for the first time.

Except for `UD` (which is not a valid country code), the country code must be
a valid [ISO-3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.

`default_country_code` defines the code to use when the identity source does not
specify a country code for a given user. It is only set for a given user whose
"country" field is empty. If a user's country is set to anything, even a country
in a format not accepted by the UMAPI, the Sync Tool will attempt to set it for
a user. This operation will only succeed if the country code is in the expected
format.

The [extension config](advanced_configuration.md#custom-attributes-and-mappings) can
be used to normalize country codes that aren't in the expected format.

## `connectors`

The `connectors` key under `directory_users` is where identity source connectors are
defined. This is done by setting the connector type as the key and the configuration
filename as the value.

Multiple connectors can be defined here (though only one can be enabled at any given time).

Example:

```yaml
directory_users:
  connectors:
    ldap: connector-ldap.yml
    csv: connector-csv.yml
    adobe_console: connector-adobe-console.yml
    okta: connector-okta.yml
```

Once an identity connector is configured, it must be enabled to be used. The connector
can be enabled in the [invocation defaults](runtime_config.md) settings or
command-line options.

## `user_identity_type`

The default identity type of new users is controlled by the `user_identity_type` option.
This can be overridden by identity options that may be available via identity source
connectors.

Valid options are `adobeID`, `enterpriseID` and `federatedID`.

Here is some [additional information](https://helpx.adobe.com/enterprise/using/identity.html)
about Adobe's different identity types.

> **Note**: in the UMAPI, Business IDs are represented by their underlying linked
> account types. In other words, there is no `businessID` type.

## `groups`

The `groups` option defines a mapping that describes rules for how identity
source groups should govern Adobe groups.

Structure:

* `groups` consists of a list of at least one mapping object
* Each mapping object has two keys
  * `directory_group` - Name of directory group to map
  * `adobe_groups` - List of zero or more Adobe groups to map

Example:

```yaml
groups:
  - directory_group: adobe-acrobat
    adobe_groups:
      - "Default Acrobat Pro DC configuration"
  - directory_group: adobe-creative
    adobe_groups:
      - "Default Photoshop CC - 100 GB configuration"
      - "Default All Apps plan - 100 GB configuration"
```

In this example, any user queried by the identity source belonging to the
source group `adobe-acrobat` is assigned the Adobe group
`Default Acrobat Pro DC configuration`.

Any user beloning to the directory group `adobe-creative` is assigned
both of these Adobe groups:

* `Default Photoshop CC - 100 GB configuration`
* `Default All Apps plan - 100 GB configuration`

Users assigned to both `adobe-acrobot` and `adobe-creative` will be assigned
all three Adobe groups in the mapping.

### Group Types

The User Management API doesn't distinguish between product profile group names
and user group names. They are treated identically when assigning group membership
to a user.

The only way the use of user groups is different is if
[automatic group creation](advanced_configuration.md#automatic-group-creation)
is enabled.

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

> \* The User Management API does not currently support the assignment of the System Admin
> role. This means that System Admins cannnot be assigned in the group mapping. This
> role can however be used in the [`exclude_adobe_groups` configuration](#exclude_adobe_groups).

**Notes about the Product Admin role:**

* It may be necessary to manually assign a user as admin to a product
before syncing users as product admins.
* The product admin role group name is case-sensitive.
* It is often necessary to assign users to at least one profile on the
same product as the admin role.

See the [UMAPI Docs](https://adobe-apiplatform.github.io/umapi-documentation/en/api/ActionsCmds.html#addRemoveAttr) for more details.

## `additional_groups`

Configures dynamic group mappings based on regular expression rules. See
[advanced config](advanced_configuration.md#additional-group-options) for more
information.

## `group_sync_options`

`group_sync_options` controls the synchronization of user groups. The only
supported option at the moment is `auto_create` which will automatically
create user groups targetted by the group mapping. See
[advanced config](advanced_configuration.md#automatic-group-creation)
for more information.

# `limits` Config

User offboarding behavior (i.e. the Adobe-only user action) can be a destructive operation.
Care should be taken with how your user sync workflow is configured.

In particular, the following `adobe_only_user_action` (or `--adobe-only-user-action`) options
can have potentially undesirable side effects.

* `preserve` - Removes mapped Adobe groups. Users offboarded with this method
  will lose access to groups/products they were provisioned with the User Sync
  Tool. User data should not be impacted.
* `remove-adobe-groups` - Removes **all** Adobe groups for offboarded users.
This will also strip offboarded users of admin privileges.
* `remove` - Remove offboarded users from the Console's Organization Users list.
  Stored Creative or Document Cloud data will not be deleted. User settings in
  other Adobe products may be affected.
* `delete` - Delete offboarded users from the underlying identity directory.
  User stored in Creative or Document Cloud will be subject to deletion.

The `max_adobe_only_users` setting is used to protect an Adobe userbase from the
`adobe_only_user_action` from operating on a large number of users. If the limit
defined by `max_adobe_only_users` is exceeded, the Adobe-only user action is
not executed at all. This can happen when something changes in the identity
source or in the User Sync Tool configuration to impact the number of Adobe-only
users identified during a sync.

`max_adobe_only_users` can be set to a hard number or a percent.

* Hard number - The limit is checked against the total number of Adobe-only users (as governed by
  the `adobe_users` setting).
* Percent - The limit is computed as a percentage of total users (as governd by
  the `adobe_users` setting).

Example scenarios:

| `max_adobe_only_users` | Total Adobe Users | Directory Users | Adobe-only Users | Outcome                                                                  |
|------------------------|-------------------|-----------------|------------------|--------------------------------------------------------------------------|
| 200                    | 1000              | 900             | 100              | Adobe-only users are processed                                           |
| 200                    | 1000              | 750             | 250              | Do not process Adobe-only users                                          |
| 20%                    | 1000              | 900             | 100              | Max is 200 (20% of 1000) so Adobe-only users are processed               |
| 20%                    | 1000              | 750             | 250              | Max of 200 (20% of 1000) exceeded, so Adobe-only users are not processed |

# `logging` Config

The User Sync Tool produces log messages describing what it is doing. Log
messages are written to the console (`stdout`) from which the tool was invoken and
optionally to a log file.

Logging behavior is governed by the `logging` option.

Example:

```yaml
logging:
  log_to_file: true
  file_log_directory: logs
  file_log_name_format: '{:%Y-%m-%d}.log'
  file_log_level: debug
  console_log_level: debug
```

## `log_to_file`

File logging is toggled by `log_to_file`. Set to `true` to write log messages to
the filesystem and `false` to suppress file logging.

If `log_to_file` is enables, then the other file-related options should be set as well.

* `file_log_directory`
* `file_log_name_format`
* `file_log_level`

## `file_log_directory`

Log files are written to files in a dedicated directory. The directory where
logs are written is set by `file_log_directory`.

This can be set to a path relative to the Sync Tool. For example, setting it
to `logs` when the Sync Tool is in the directory `/home/user-sync` will write
log files to the directory `/home/user-sync/logs`.

`file_log_directory` can also be set to an absolute path.

## `file_log_name_format`

File log messages are appended to the file defined by `file_log_name_format`.
This can be set to a static filename such as `user-sync.log`. Or date/time
information can be encoded using curly braces `{}`.

Any of [these formatting codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
can be used.

For example, to set the filename to the date in `yyyy-mm-dd` format,
`file_log_name_format` can be set to `{:%Y-%m-%d}.log`.

> **Note**: The date is formatted at the beginning of the sync workflow.

Log files that don't exist will be created automatically.

## `file_log_level` and `console_log_level`

These options control the verbosity for log files and console (`stdout`)
output respectively.

Each level adds more information to the logs. These are the supported levels,
in order from least verbose to most verbose. The higher verbosity levels
include messages from lower levels. In other words `debug` includes all other
message types.

1. `critical`

   Only log critical errors that generally impact the overall sync process.

2. `error`

   Log errors of any kind, even those that may not halt or negatively impact
   sync.

3. `warning`

   Warnings include messages that warrant attention but are not serious. Reasons
   include deprecated functionality, missing identity source data, etc.

4. `info` (default)

   Informational log messages. General information around sync behavior
   including summary info.
   
5. `debug`

   Any lower-level debug information: configuration options, raw API call
   payloads, etc. This information can be critical for debugging issues with
   User Sync Tool config, but can increase log file sizes significantly.

# `invocation_defaults` Config

See [Runtime Config](runtime_config.md) for information about the Sync Tool's
`invocation_default` options and how they interact with the tool's
command-line options.

---

[Previous Section](setup_and_installation.md)  \| [Next Section](connect_adobe.md)
