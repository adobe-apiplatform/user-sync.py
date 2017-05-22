---
layout: page
title: User Manual
lang: en
nav_link: Configuring the User Sync Tool
nav_level: 1
nav_order: 30
---


## Configuring the User Sync Tool

The operation of the User Sync tool is controlled by a set of
configuration files with these file names, located (by default) in the same
folder as the command-line executable.

| Configuration File | Purpose |
|:------|:---------|
| user-sync-config.yml | Required. Contains configuration options that define the mapping of directory groups to Adobe product configurations and user groups, and that control the update behavior.  Also contains references to the other config files.|
| connector&#x2011;umapi.yml&nbsp;&nbsp; | Required. Contains credentials and access information for calling the Adobe User Management API. |
| connector-ldap.yml | Required. Contains credentials and access information for accessing the enterprise directory. |


If you need to set up access to Adobe groups in other organizations that
have granted you access, you can include additional configuration
files. For details, see the
[advanced configuration instructions](#accessing-groups-in-other-organizations)
below.

### Setting up configuration files

Examples of the three required files are provided in the `config
files - basic` folder in the release artifact
`example-configurations.tar.gz`:

```text
1 user-sync-config.yml
2 connector-umapi.yml
3 connector-ldap.yml
```

To create your own configuration, copy the example files to your
User Sync root folder and rename them (to get rid of the leading
number). Use a plain-text editor to customize the your copied
configuration files for your environment and usage model. The
examples contain comments showing all possible configuration
items. You can uncomment items that you need to use.

Configurations files are in [YAML format](http://yaml.org/spec/)
and use the `yml` suffix. When editing YAML, remember some
important rules:

- Sections and hierarchy in the file are based on
indentation. You must use SPACE characters for indentation. Do
not use TAB characters.
- The dash character (-) is used to form a list of values. For
example, the following defines a list named “adobe\_groups”
with two items in it.

```YAML
adobe_groups:
  - Photoshop Users
  - Lightroom Users
```

Note that this can look confusing if the list has only one item
in it.  For example:

```YAML
adobe_groups:
  - Photoshop Users
```

### Create and secure connection configuration files

The two connection configuration files store the credentials that
give User Sync access to the Adobe Admin Console and to your
enterprise LDAP directory. In order to isolate the sensitive
information needed to connect to the two systems, all actual
credential details are confined to these two files. **Be sure to
secure them properly**, as described in the
[Security Considerations](#security-considerations) section of
this document.

There are three techniques supported by User Sync for securing credentials.

1. Credentials can be placed in the connector-umapi.yml and connector-ldap.yml files directly and the files protected with operating system access control.
2. Credentials can be placed in the operating system secure credential store and referenced from the two configuration files.
3. The two files in their entirety can be stored securely or encrypted and a program that returns their contents is referenced from the main configuration file.


The example configuration files include entries that illustrate each of
these techniques.  You would keep only one set of configuration items
and comment out or remove the others.

#### Configure connection to the Adobe Admin Console (UMAPI)

When you have obtained access and set up an integration with User
Management in the Adobe I/O
[Developer Portal](https://www.adobe.io/console/), make note of
the following configuration items that you have created or that
have been assigned to your organization:

- Organization ID
- API Key
- Client Secret
- Technical Account ID
- Private Certificate

Open your copy of the connector-umapi.yml file in a plain-text
editor, and enter these values in the “enterprise” section:

```YAML
enterprise:
  org_id: "Organization ID goes here"
  api_key: "API key goes here"
  client_secret: "Client Secret goes here"
  tech_acct: "Tech Account ID goes here"
  priv_key_path: "Path to Private Certificate goes here"
```

**Note:** Make sure you put the private key file at the location
specified in `priv_key_path`, and that it is readable only to the
user account that runs the tool.

In User Sync 2.1 or later there is an alternative to storing the private key in a separate file; you can place
the private key directly in the configuration file.  Rather than using the
`priv_key_path` key, use `priv_key_data` as follows:

	  priv_key_data: |
	    -----BEGIN RSA PRIVATE KEY-----
	    MIIJKAIBAAKCAge85H76SDKJ8273HHSDKnnfhd88837aWwE2O2LGGz7jLyZWSscH
	    ...
	    Fz2i8y6qhmfhj48dhf84hf3fnGrFP2mX2Bil48BoIVc9tXlXFPstJe1bz8xpo=
	    -----END RSA PRIVATE KEY-----



#### Configure connection to your enterprise directory

Open your copy of the connector-ldap.yml file in a plain-text
editor, and set these values to enable access to your enterprise
directory system:

```
username: "username-goes-here"
password: "password-goes-here"
host: "FQDN.of.host"
base_dn: "base_dn.of.directory"
```

### Configuration options

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
[Protecting Specific Accounts from User Sync Deletion](#protecting-specific-accounts-from-user-sync-deletion)
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

#### Configure connection files

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

#### Configure group mapping

Before you can synchronize user groups and entitlements, you must
create user groups and product configurations in the
Adobe Admin Console, and corresponding groups in your enterprise
directory, as described above in
[Set up product-access synchronization](#set-up-product-access-synchronization).

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

#### Configure limits

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

For example:

```YAML
limits:
  max_adobe_only_users: 200
```

This configuration causes User Sync to check if more than
200 user accounts present in Adobe are not found in the enterprise directory (as filtered),
and if so no existing Adobe accounts are updated and an error message is logged.

####  Configure logging

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

### Example configurations

These examples show the configuration file structures and
illustrate possible configuration values.

##### user-sync-config.yml

```YAML
adobe_users:
  connectors:
    umapi: connector-umapi.yml
  exclude_identity_types:
    - adobeID

directory_users:
  user_identity_type: federatedID
  default_country_code: US
  connectors:
    ldap: connector-ldap.yml
  groups:
    - directory_group: Acrobat
      adobe_groups:
        - Default Acrobat Pro DC configuration
    - directory_group: Photoshop
      adobe_groups:
        - "Default Photoshop CC - 100 GB configuration"
        - "Default All Apps plan - 100 GB configuration"
        - "Default Adobe Document Cloud for enterprise configuration"
        - "Default Adobe Enterprise Support Program configuration"

limits:
  max_adobe_only_users: 200

logging:
  log_to_file: True
  file_log_directory: userSyncLog
  file_log_level: debug
  console_log_level: debug
```

##### connector-ldap.yml

```YAML
username: "LDAP_username"
password: "LDAP_password"
host: "ldap://LDAP_ host"
base_dn: "base_DN"

group_filter_format: "(&(objectClass=posixGroup)(cn={group}))"
all_users_filter: "(&(objectClass=person)(objectClass=top))"
```

##### connector-umapi.yml

```YAML
server:
  # This section describes the location of the servers used for the Adobe user management. Default is:
  # host: usermanagement.adobe.io
  # endpoint: /v2/usermanagement
  # ims_host: ims-na1.adobelogin.com
  # ims_endpoint_jwt: /ims/exchange/jwt

enterprise:
  org_id: "Org ID goes here"
  api_key: "API key goes here"
  client_secret: "Client secret goes here"
  tech_acct: "Tech account ID goes here"
  priv_key_path: "Path to private.key goes here"
  # priv_key_data: "actual key data goes here" # This is an alternative to priv_key_path
```

### Testing your configuration

Use these test cases to ensure that your configuration is working
correctly, and that the product configurations are correctly
mapped to your enterprise directory security groups . Run the
tool in test mode first (by supplying the -t parameter), so that
you can see the result before running live.

#####  User Creation

1. Create one or more test users in enterprise directory.

2. Add users to one or more configured directory/security groups.

3. Run User Sync in test mode. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)

3. Run User Sync not in test mode. (`./user-sync --users all --process-groups --adobe-only-user-action exclude`)

4. Check that test users were created in Adobe Admin Console.

##### User Update

1. Modify group membership of one or more test user in the directory.

1. Run User Sync. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)

2. Check that test users in Adobe Admin Console were updated to
reflect new product configuration membership.

#####  User Disable

1. Remove or disable one or more existing test users in your
enterprise directory.

2. Run User Sync. (`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)

3. Check that users were removed from configured product
configurations in the Adobe Admin Console.

4. Run User Sync to remove the users (`./user-sync -t --users all --process-groups --adobe-only-user-action delete`) Then run without -t.  Caution: check that only the desired user was removed when running with -t.  This run (without -t) will actually delete users.

5. Check that the user accounts are removed from the Adobe Admin Console.

---
