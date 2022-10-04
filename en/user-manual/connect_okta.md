---
layout: default
lang: en
nav_link: Sync From Okta
title: Syncing Users From Okta
nav_level: 2
nav_order: 33
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

See (TODO add link) Security Recommendations for more information.

# User Filter Options

## `group_filter_format`

## `all_users_filter`

# General Options

# Attribute Mapping Options

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
