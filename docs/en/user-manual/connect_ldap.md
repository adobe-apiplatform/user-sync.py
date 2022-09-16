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

### Simple

```yml
username: user@example.com
password: password13
host: "ldaps://my-ldap-fdqn.example.com"
base_dn: "base_dn.of.directory"
```

### Anonymous

### Kerberos

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
