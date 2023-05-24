---
layout: default
lang: en
nav_link: Sync From Okta
title: Syncing Users From Okta
nav_level: 2
nav_order: 43
parent: user-manual
page_id: connect-okta
---

[Previous Section](connect_ldap.md)  \| [Next Section](sync_from_console.md)

# Syncing Users From Okta
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

The Okta connector uses an [Okta](https://www.okta.com) tenant as a source for user identity
and group membership.  Since Okta always uses email addresses as the unique ID for users,
the Okta connector does not support username-based federation.

Okta customers must obtain an API token for use with the Okta Users API.
See [Okta's Developer Documentation](http://developer.okta.com/docs/api/getting_started/api_test_client.html)
for more information.

# Initial Setup

Okta support is facilitated by the Okta connector. The Okta connector requires its own config
file (`connector-okta.yml`). This config file must be referenced in `user-sync-config.yml` to
enable the connector.

First, obtain a [config file template](https://github.com/adobe-apiplatform/user-sync.py/blob/v2/examples/config%20files%20-%20basic/connector-okta.yml).
Copy it to your User Sync Tool directory.

Then, add the config to `user-sync-config.yml` under `directory_users.connectors`:

```yaml
directory_users:
  connectors:
    okta: connector-okta.yml
```

See [below](#runtime) to learn how to invoke the User Sync Tool with the Okta connector.

# Authentication

The Okta connector uses the Okta API to retrieve user and group information. In order to use the
connector, an API connection must be defined.

The connector currently only supports Okta's legacy API key for authentication. Refer to
[their documentation](https://developer.okta.com/docs/guides/create-an-api-token/main/) for
information about creating a token. OAuth is not supported at this time.

To set up authentication, configure the `host` and `api_token` options.

## `host`

The `host` option should be set to the hostname of the Okta instance. Just the hostname (sans `https://`) is needed.

```yaml
host: example.oktapreview.com
```

## `api_token`

`api_token` is used to configure the token for accessing the Okta API. Refer to
[Okta's documentation](https://developer.okta.com/docs/guides/create-an-api-token/main/)
for information on creating the token.

The token can be specified in plaintext in the config file. If you do this, you are responsible
for keeping the file and server environment secure.

```yaml
api_token: "okta_api_token"
```

The recommended way to store the token is to save it to the OS keyring and reference
the key in the config file using the `secure_api_token_key` option.

```yaml
secure_api_token_key: "UST Okta Token"
```

See [Security Recommendations](security.md#secure-credential-storage) for more
information.

# User Filter Options

These options are used to filter users and groups. Their defaults are generally sufficient
for most use cases but can be customized if needed.

## `group_filter_format`

The `group_filter_format` option specifies a template string used when querying users
for a group.

By default it is set to `{group}`. The name of a given group is inserted in between
the curly braces.

## `all_users_filter`

`all_users_filter` controls which users are considered in-scope for sync from the Okta connector.
It should be set to a Python statement that returns `True` or `False`. Users where the
filter evaluates `True` are included in sync. Users where it evaluates `False` are
filtered out.

Any user attribute returned from Okta's "List Group Members" call can be used in the filter
See [their API docs](https://developer.okta.com/docs/reference/api/groups/#response-example-12)
for more info.

# General Options

## `user_identity_type`

The `user_identity_type` option can be used to override the `identity_type` setting in `user-sync-config.yml`.
This can be useful if the same root configuration file is used with different identity connectors. If this
option isn't set then the identity type for user sync will be governed by the top-level `identity_type` setting.

**Note:** This setting can be overridden by `user_identity_type_format`.

## `string_encoding`

The `string_encoding` option defines the character encoding used when formatting Okta values.

Default is `utf8`.

# Attribute Mapping Options

This group of options govern how attributes are mapped. These generally don't need to be customized
for the Okta, but can be in case customization is needed.

These options are named identically to the attribute mapping options in the LDAP config
and behave similarly.

See the [LDAP config page](connect_ldap.md#attribute-mapping-options) for more information.


# Runtime

In order to use the Okta connector, you will need to specify the `--connector okta`
command-line parameter.  (LDAP is the default connector.)  In addition because the
Okta connector does not support fetching all users, you must additionally specify
a `--users` command line option of `group` or `mapped`.  All other User Sync
command-line parameters have their usual meaning.

# Extension Support

Okta sync can use extended groups, attributes and after-mapping hooks.  The names of extended attributes must be valid Okta profile fields.

---

[Previous Section](connect_ldap.md)  \| [Next Section](sync_from_console.md)
