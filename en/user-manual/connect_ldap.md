---
layout: default
lang: en
nav_link: Connect to LDAP
nav_level: 2
nav_order: 32
parent: user-manual
page_id: connect-ldap
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

```yaml
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

```yaml
base_dn: DC=example,DC=com
```

It is important to note that all users and groups that the Sync Tool may query must be contained in the scope
set by `base_dn`.

In some cases, perhaps when querying a global catalog, the `base_dn` may be left blank.

```yaml
base_dn: ""
```

### Simple Auth

`simple` authentication uses a username and password to authenticate with an LDAP server.

If `username` and `password` (or `secure_password_key`) are both specified, then the `authentication_method`
option does not need to be set. The configuration system will assume you are using `simple` auth. You
can set the method explicitly if desired with `authentication_method: simple`.

Example:

```yaml
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

```yaml
secure_password_key: my_ldap_password
# password:
```

See [Security Recommendations](deployment_best_practices.md#security-recommendations) for more information.

### Anonymous Auth

The `anonymous` auth method makes the LDAP connector perform an anonymous (un-authenticated) query against
the LDAP source. The server will return an error if anonymous queries are not supported. To enable anonymous
queries, simply omit the `username` field.

```yaml
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


```yaml
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

```yaml
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

```yaml
all_users_filter: "(&(objectClass=user)(objectCategory=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
```

This query filters out any object that isn't a user account or is disabled.

A different LDAP system such as OpenLDAP may use a different query.

```yaml
all_users_filter: "(&(objectClass=person)(objectClass=top))"
```

### `group_filter_format`

The `group_filter_format` options defines the query used by the LDAP connector to get the DN of a group for a given
common name. This is a necessary step when running user sync with group mapping and processing enabled (the most common
use case).

The default setting is configured to work with either Active Directory or OpenLDAP. This may need to be
customized for other types of LDAP systems.

The group common name is interpolated into the query string using `{group}` marker.

```yaml
group_filter_format: "(&(|(objectCategory=group)(objectClass=groupOfNames)(objectClass=posixGroup))(cn={group}))"
```

### `group_member_filter_format`

`group_member_filter_format` defines the query used to identify all users belonging to a given group based
on the group DN. This query is used when group mapping and processing are enabled.

The default setting uses the `memberOf` attribute, which is specific to Active Directory. This setting may
need to be customized to work with other LDAP systems.

The marker `{group_dn}` interpolates the DN of the group.

```yaml
group_member_filter_format: "(memberOf={group_dn})"
```

**Note**: The default Active Directory query shown above will only return users that are direct members
of the group. The query can be modified to include users in nested subgroups if the LDAP server supports
it. Here is an example for Active Directory:

```yaml
group_member_filter_format: "(memberOf:1.2.840.113556.1.4.1941:={group_dn})"
```

Note that this may increase the time it takes to retrieve users.

### `dynamic_group_member_attribute`

If `additional_groups` rules are defined in `user-sync-config.yml`, the `dynamic_group_member_attribute`
option defines the attribute to use when identifying a user's member groups. It is set to `memberOf` by
default (which works for Active Directory).

```yaml
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

```yaml
# must disable (comment out) group_member_filter_format
# group_member_filter_format: "(memberOf={group_dn})"

two_steps_lookup:
  group_member_attribute_name: "member"
  nested_group: True
```

## Attribute Mapping Options

This group of options govern how attributes are mapped. The most important options to look at are `user_email_format`
and `user_username_format`. These attributes determine how users are identified in the Admin Console. They
impact Single Sign-On for federated users and affect how users are identified for User Sync.

Each of these options use an interpolation convention to inject the value of a variably-named LDAP attribute.

For example, `user_country_code_format` looks like this by default:

```yaml
user_country_code_format: "{c}"
```

The `c` attribute is the default country name or country code attribute in Active Directory. If a user is
retrieved from the LDAP system with a `c` attribute of `GB`, then the User Sync Tool will look at the column
name defined between the curly braces, get the `c` attribute value `GB` from the LDAP user record, and inject the
value in the user's `country` attribute, setting the user's country code to `GB`.

This syntax can be used to inject multiple fields to create composite values. For example, if you want to
build the username from two fields, you might do something like this:

```yaml
user_username_format: "{field1}_{field2}"
```

This will inject the values of attributes `field1` and `field2` into the template string, which contains
an underscore (`_`) as a separator. So if `field1 = abc` and `field2 = 123` then the interpolated result
would be `username = abc_123`

The curly-brace syntax can also be omitted for cases where a value should be hard-coded.

```yaml
user_domain_format: "example.com"
```

### `user_email_format`

`user_email_format` defines the attribute used to set an Adobe user's email address. This field can serve
as a primary identifier for a user depending on the circumstances.

* Serves as primary ID for `adobeID` and `enterpriseID` users since those users cannot have usernames that
differ from `email`
* On any Adobe login page, the email address determines
  * Account type availability (Personal or Company/School account)
  * The "profile picker" widget when logging with a Business ID
* For `federatedID` users, the email address determines the identity provider in the IDP redirect during login
flow
* Email address is also used in any sharing or collaboration features in Creative or Document Cloud

This option is set to `{mail}` by default which is the default in Active Directory.

```yaml
user_email_format: "{mail}"
```

### `user_username_format`

The `user_username_format` option maps an Adobe user's username field. For `federatedID` users, the username
can be set to a different value from the email address. **Note:** do not set this option for `adobeID` or
`enterpriseID` users. The username will always be set to the user's email address for those types.

The username is used in the SSO login workflow. It should be mapped to the field used to populate `NameID`
in the SAML payload.

The username can take two forms:

* **Email-type** e.g. `jdoe@example.com`. The email-type username does not necessarily need to correspond to
a live email address. It just needs to resemble an email address. If you want to use email-type usernames, it
is important to know that the username's domain must be claimed to the same directory as the user's email address.
Otherwise user login will fail. For Active Directory, the suggested field to map is `userPrincipalName`.
* **Non-email** e.g. `jdoe`. An alphanumeric username that may correspond to something like a user's internal user ID
or LAN login name. For this type, the Admin Console still needs to know the domain associated with the username, so the
domain must be explicitly mapped using the `user_domain_format` option. The suggested field to map for Active Directory is
`sAMAccountName`.

Mapping the username separately gives the UST a way to update a user's email address.

* The `update_user_info` option in `user-sync-config.tml` must be `True` (or invoke with the `--update-user-info` CLI option)
* The username must not change

If those conditions are met, then the UST will keep a user's email address up-to-date.

### `user_domain_format`

If you are syncing users with non-email usernames, the domain must be set or mapped in the `user_domain_format` field.
This may be dynamically mapped to an LDAP attribute if one exists.

```yaml
user_domain_format: "{domain}"
```

Or if such an attribute isn't available then it can be hard-coded.

```yaml
# set the domain of *all users* to "example.com"
user_domain_format: "example.com"
```

**Note:** If `user_domain_format` is enabled, then the username for **all** users must be in non-email format. Any
user with an email-type username will fail to sync.

### `user_given_name_format`

A user's given name ("First Name" in Admin Console nomenclature) can be mapped with `user_given_name_format`.

The default value is `"{givenName}"` - the default attribute in Active Directory.

### `user_surname_format`

A user's surname ("Last Name" in Admin Console nomenclature) can be mapped with `user_surname_format`.

The default value is `"{sn}"` - the default attribute in Active Directory.

### `user_country_code_format`

`user_country_code_format` maps the user's country code.

The User Management API requires the country code field be a valid [ISO-3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
code.

The country code is important - it governs key aspects of cloud storage and service availability. It must
be set for all users, but assignment may be deferred depending on user type.

* For `adobeID` and `enterpriseID`, the country code can be set to `UD` to mark the country "undefined".
Users with `UD` country codes will be prompted to specify their own country code upon login.
* Country code is required for `federatedID` users and cannot be set to `UD`.

By default, the LDAP connector looks at the `c` field, which is the default country attribute
for Active Directory. AD does not place any formatting requirements on this field, so it isn't
uncommon to see users with country fields in different formats such as `USA` or `United States`.

There are a few different solutions to this. One possible solution is to hard-code the country value
in the `user_country_code_format` option.

```yaml
user_country_code_format: US
```

Note that this will set the same code for every user, overriding anything read from `c` or the equivalent
attribute. 

It may be a better option to use the (TODO: add link) extension config to dynamically normalize the
country code.

### `user_identity_type_format`

The `user_identity_type_format` can be used to dynamically set the identity type. It maps an LDAP attribute
to a user's identity type. If this option is used it will override the `user_identity_type` option
defined in the LDAP connector config (which itself overrides `user_identity_type` in `user-sync-config.yml`).

For example, an LDAP system with a theoretical `idType` attribute that could be set to `adobe`, `enterprise`
or `federated` might be used in this manner:

```yaml
user_identity_type_format: "{idType}ID"
```

However, this option is not typically used. It's a better practice to ensure that all users from a given identity
source have the same identity type.

---

[Previous Section](connect_adobe.md)  \| [Next Section](command_parameters.md)
