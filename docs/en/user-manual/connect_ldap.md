---
layout: default
lang: en
nav_link: Connect to LDAP
nav_level: 2
nav_order: 32
---

[Previous Section](connect_adobe.md)  \| [Next Section](command_parameters.md)

# Connecting To LDAP
{:."no_toc"}

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

## Overview

The User Sync Tool can synchronize user and entitlement group information from a variety of sources. The recommended
and most common source is an LDAP system such as Active Directory.

User sync from an LDAP source is handled with the `ldap` identity connector. The `ldap` connector is configured with the
config file `connector-ldap.yml`, which defines credentials to access the LDAP system as well as some options to customize
LDAP query structures and attribute mapping.

`connector-ldap.yml` is one of the three core configuration files generated when using the `init` or `example-config` command.

## Authentication

The `ldap` connector supports four authentication methods. This is set with the `authentication_method` option.

* `simple` - Authenticate with username and password. Password can be set in plain text or stored in the OS keyring
securely. This is the default method if `username` is specified.
* `anonymous` - Read users and groups without authenticating, if the LDAP server supports it. This is the default
methof if `username` is not specified.
* `kerberos` (**recommended**) - Relies on authenticated server login session to access LDAP securely. Read
further for more information.
* `ntlm` - Authenticates LDAP session using NTLM. User should be specified in the format `DOMAIN\USER`. Password
can be set to NTLM hash instead of plaintext password.

### `host` Option

The `host` option should take the form `(ldap|ldaps)://server.host[:port]`. The protocol should be `ldap` if
the connection should be plain (non-SSL). Use `ldaps` to force a secure (LDAP over SSL) connection.

The `host` domain portion should generally be the Full-Qualified Domain Name (FDQN).

The port compenent can be omitted if the server listens on the standard ports - `389` for plain connections
or `636` for LDAPS.

Append the port (with a colon `:`) to the hostname if connecting to a non-standard port (such as the Active Directory
global catalog ports - 3268/3269).

Example:

```yml
# connect to LDAPS global catalog port
host: ldaps://global-catalog.example.com:3269
```

### `base_dn` Option

LDAP queries generally require a base distinguished name (DN). A DN is a type of identifier that uniquely
identifies any object in an LDAP system. Because of the hierarchical nature of LDAP, a query must be
rooted in a "scope" in which to search an object tree. The `base_dn` option sets this scope in the LDAP
connector config.

In other words, the `base_dn` points to the root object from which to conduct an LDAP query.

For best results, this should generally be set to the root domain of the directory. For example, if the
domain is `example.com` then the `base_dn` would be set to `DC=example,DC=com`.

```yml
base_dn: DC=example,DC=com
```

It is important to note that all users and groups that the Sync Tool may query must be contained in the scope
set by `base_dn`.

In some cases, perhaps when querying a global catalog, the `base_dn` may be left blank.

```yml
base_dn: ""
```

### Simple Auth

`simple` authentication uses a username and password to authenticate with an LDAP server.

If `username` and `password` (or `secure_password_key`) are both specified, then the `authentication_method`
option does not need to be set. The configuration system will assume you are using `simple` auth. You
can set the method explicitly if desired with `authentication_method: simple`.

Example:

```yml
username: user@example.com
password: password13
host: "ldaps://my-ldap-fdqn.example.com"
base_dn: DC=example,DC=com
```

Depending on the type of LDAP server, the username may take different forms. Modern Active Directory servers
generally accept the User Principal Name of the account, e.g. `user@example.com`. If that doesn't work,
the form `DOMAIN\username` might be accepted. Other LDAP systems may accept a plain `username`.

The password may be saved in plaintext. This is done at your own risk and depends on the security of the config
file and server environment.

The password can be saved securely to the OS keyring (e.g. Windows Credential Manager) and referenced by the
field `secure_password_key`. If the secure key option is specified, then the `password` option should be
omitted. Example:

```yml
secure_password_key: my_ldap_password
# password:
```

See [Security Recommendations](deployment_best_practices.md#security-recommendations) for more information.

### Anonymous Auth

The `anonymous` auth method makes the LDAP connector perform an anonymous (un-authenticated) query against
the LDAP source. The server will return an error if anonymous queries are not supported. To enable anonymous
queries, simply omit the `username` field.

```yml
# username: user@example.com
host: "ldaps://my-ldap-fdqn.example.com"
base_dn: DC=example,DC=com
```

If `username` is omitted, then the `authentication_method` option does not need to be set. The configuration
system will assume you are using `anonymous` auth. You can set the method explicitly if desired with
`authentication_method: anonymous`.


### Kerberos Auth

The `kerberos` authentication method uses Kerberos to use a user's authenticated session to securely connect
to the LDAP system. For Kerberos auth to work, the user account running the Sync Tool must be authenticated
with the directory system specified in the LDAP connector config. Assuming the LDAP connector can find
a valid ticket to provide, the LDAP connector can authenticate with the LDAP server with no username or
password.

The easiest way to get this to work is to run the User Sync Tool on a Windows server and connect the LDAP
connector to Active Directory. The server should be joined to the Active Directory domain and the account
running the sync tool should be authenticated with the Active Directory domain controller.

If these conditions are met, then configuring the LDAP connection is simple.


```yml
host: "ldaps://my-ldap-fdqn.example.com"
base_dn: DC=example,DC=com

# auth method must be set here to avoid "anonymous" auth
authentication_method: kerberos
```

This method may work on Linux machines and/or non-Active-Directory LDAP systems. These options have not been
tested.

**Note:**

The `host` may need to be changed depending on how the domain is set up. If you have trouble using the domain's
FDQN, you can find the server your system is connecting do by running this command in a Windows Command prompt:

```
> echo %logonserver%
```

### NTLM Auth

Use the authentication method option `ntlm` to use NTLM authentication. The `password` field can contain either
the plaintext password or the NTLM hash. Either can optionally be secured in the OS keychain and referenced
with the option `secure_password_key`.

**Note:** Username should be specified in the format `DOMAIN\USER`.

```yml
username: EXAMPLE\User
password: "[NTLM hash]"
host: "ldaps://my-ldap-fdqn.example.com"
base_dn: DC=example,DC=com
```

## General Options

### `user_identity_type`

The `user_identity_type` option can be used to override the `identity_type` setting in `user-sync-config.yml`.
This can be useful if the same root configuration file is used with different identity connectors. If this
option isn't set then the identity type for user sync will be governed by the top-level `identity_type` setting.

**Note:** This setting can be overridden by `user_identity_type_format`.

### `string_encoding`

The `string_encoding` option defines the character encoding used in the LDAP system.

Default is `utf8`.

## LDAP Query Options

These options govern LDAP query behavior.

### `search_page_size`

Controls the size of LDAP query pages. Default is `1000` records.

### `all_users_filter`

The `all_users_filter` setting defines the LDAP query used to query all users from the LDAP system. The default
is geared at Active Directory.

```yml
all_users_filter: "(&(objectClass=user)(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
```

This query filters out any object that isn't a user account or is disabled.

A different LDAP system such as OpenLDAP may use a different query.

```yml
all_users_filter: "(&(objectClass=person)(objectClass=top))"
```

### `group_filter_format`

The `group_filter_format` options defines the query used by the LDAP connector to get the DN of a group for a given
common name. This is a necessary step when running user sync with group mapping and processing enabled (the most common
use case).

The default setting is configured to work with either Active Directory or OpenLDAP. This may need to be
customized for other types of LDAP systems.

The group common name is interpolated into the query string using `{group}` marker.

```yml
group_filter_format: "(&(|(objectCategory=group)(objectClass=groupOfNames)(objectClass=posixGroup))(cn={group}))"
```

### `group_member_filter_format`

`group_member_filter_format` defines the query used to identify all users belonging to a given group based
on the group DN. This query is used when group mapping and processing are enabled.

The default setting uses the `memberOf` attribute, which is specific to Active Directory. This setting may
need to be customized to work with other LDAP systems.

The marker `{group_dn}` interpolates the DN of the group.

```yml
group_member_filter_format: "(memberOf={group_dn})"
```

**Note**: The default Active Directory query shown above will only return users that are direct members
of the group. The query can be modified to include users in nested subgroups if the LDAP server supports
it. Here is an example for Active Directory:

```yml
group_member_filter_format: "(memberOf:1.2.840.113556.1.4.1941:={group_dn})"
```

Note that this may increase the time it takes to retrieve users.

### `dynamic_group_member_attribute`

If `additional_groups` rules are defined in `user-sync-config.yml`, the `dynamic_group_member_attribute`
option defines the attribute to use when identifying a user's member groups. It is set to `memberOf` by
default (which works for Active Directory).

```yml
dynamic_group_member_attribute: "memberOf"
```

### `two_steps_lookup`

Some LDAP systems do not support a `memberOf`-type group membership lookup predicate. `two_steps_lookup` enables
a two-step group lookup workflow.

Workflow for each directory group:

1. Retrieve group info according to group mapping
2. Get list of users defined in group's `group_member_attribute_name`
3. Filter user list according to `all_users_filter`
4. (optional) If `nested_group` enabled, then recurse into subgroups (if present) and repeat steps 1-3
for users belonging to each subgroup

Two-step config consists of two sub-options.

* `group_member_attribute_name` - attribute of the group that contains list of group members (default: `member`).
If this option is enabled, then the `group_member_filter_format` option must be disabled.
* `nested_group` - if `True`, then recurse into subgroups. Note that this may increase the time it takes
to retrieve users and groups.

Example:

```yml
# must disable (comment out) group_member_filter_format
# group_member_filter_format: "(memberOf={group_dn})"

two_steps_lookup:
  group_member_attribute_name: "member"
  nested_group: True
```

## Attribute Mapping Options

### `user_identity_type_format`

### `user_email_format`

### `user_username_format`

### `user_domain_format`

### `user_given_name_format`

### `user_surname_format`

### `user_country_code_format`

## Working with Username-Based Login

On the Adobe Admin Console, you can configure a federated domain to use email-based user login names or username-based (i.e., non-email-based) login.   Username-based login can be used when email addresses are expected to change often or your organization does not allow email addresses to be used for login.  Ultimately, whether to use username-based login or email-based login depends on a company's overall identity strategy.

To configure User Sync to work with username logins, you need to set several additional configuration items.

In the `connector-ldap.yml` file:

- Set the value of `user_username_format` to a value like '{attrname}' where attrname names the directory attribute whose value is to be used for the user name.
- Set the value of `user_domain_format` to a value like '{attrname}' if the domain name comes from the named directory attribute, or to a fixed string value like 'example.com'.

When processing the directory, User Sync will fill in the username and domain values from those fields (or values).

The values given for these configuration items can be a mix of string characters and one or more attribute names enclosed in curly-braces "{}".  The fixed characters are combined with the attribute value to form the string used in processing the user.

For domains that use username-based login, the `user_username_format` configuration item should not produce an email address; the "@" character is not allowed in usernames used in username-based login.

If you are using username-based login, you must still provide a unique email address for every user, and that email address must be in a domain that the organization has claimed and owns. User Sync will not add a user to the Adobe organization without an email address.

## Syncing Email-based Users with Different Email Address

Some organizations must authenticate users with an internal-facing
email-type ID such as user principal name, but wish to allow users to
user their public-facing email address to log into Adobe products and
use collaboration features.

Internally, the Adobe Admin Console maintains a distinction between a
user's email-type username and their email address.  These fields are
normally set to the same value, but the Admin Console allows the
email address to differ from the username.  The User Management API
also supports the creation, update, and deletion of users that have
different usernames and email addresses.

**Note:** Any domain used in the email address field **must** be
claimed and added to an Adobe identity directory.

To use this functionality in the Sync Tool, simply specify both the
`user_email_format` and the `user_username_format` options in
`connector-ldap.yml`.

```yaml
user_email_format: "{mail}"
user_username_format: "{userPrincipalName}"
```

In this scenario, the `user_username_format` option must map to a field
that will always contain an email-type identifier (it does not need
to be a live, working email address).  Users with non-email values
will fail to be validated and synced.


---

[Previous Section](connect_adobe.md)  \| [Next Section](command_parameters.md)
