---
layout: default
lang: en
title: Syncing From the Admin Console
nav_link: Sync From Admin Console
nav_level: 2
nav_order: 44
parent: user-manual
page_id: sync-from-console
---

[Previous Section](connect_okta.md)  \| [Next Section](sync_from_csv.md)

# Syncing From the Admin Console
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

The User Sync Tool can use the Admin Console as an identity connector. This can
be used to manage users for a trustee directory when the parent directory uses
Azure AD sync or Google Sync, or to manage [Sign Enterprise
Users](sign_sync.md#sign-enterprise).

# Initial Setup

The connector can be enabled by adding `adobe_console` to
`directory_users.connectors` in `user-sync-config.yml`.

```yaml
directory_users:
  connectors:
    adobe_console: connector-adobe-console.yml
```

A template config file can be obtained
[here](https://github.com/adobe-apiplatform/user-sync.py/blob/v2/examples/config%20files%20-%20basic/connector-adobe-console.yml).

To invoke the sync tool with the `adobe_console` connector, do one of the
following.

* Specify `adobe_console` as the `connector` in `invocation_options` inside
  `user-sync-config.yml`.

  ```yaml
  invocation_options:
    connector: adobe_console
  ```
* Run the Sync Tool with the option `--connector adobe_console`

  ```
  $ ./user-sync --connector adobe_console
  ```

# Configuring a Connection

All UMAPI sync setups require at least one UMAPI connector configuration. This
primary connection config should be called `connector-umapi.yml`.

Like the UMAPI connector, the Admin Console Connector requires a [UMAPI
integration on the Adobe Developer
Console](setup_and_installation.md#adobe-developer-console-setup).

> **Note:** This guide covers [OAuth
> Server-to-Server](https://developer.adobe.com/developer-console/docs/guides/authentication/ServerToServerAuthentication/implementation/)
> authentication. JWT-based authentication is **deprecated**. If you need to
> migrate your integration, please refer to [this
> guide](connect_adobe.md#migrating-from-jwt-to-server-to-server). It is geard
> to the UMAPI connector, but the procedure for migrating Admin Console
> connector config is very similar.

`connector-adobe-console.yml` defines the following top-level config keys.

* `server` - Override default identity and UMAPI endpoints (generally not
  needed) and customize connection timeout and retry settings
* `integration` - Define UMAPI credentials (either in-line plaintext or
  references to OS keyring objects)
* `identity_type_filter` - Tells the connector to only include the identity type
  specified (`adobeID`, `enterpriseID` or `federatedID`)
* `authentication_method` - Governs authentication method. Supports `oauth` for
  Server-to-Server connections and `jwt` for deprecated JWT connections. Default
  for compatibility reasons is `jwt`.

## `server` Settings

The `server` settings do not generally need to be customized. `timeout` and
`retry` settings can be customized if the Sync Tool is running on a high-latency
network connection.

> **Note:** The options `ims_host` and `ims_endpoint_jwt` are deprecated in
> favor of the options `auth_host` and `auth_endpoint`. These options serve the
> same purpose as their deprecated counterparts.

## `integration` Settings

The `integration` key defines credentials used to authenticate with the User
Management API. The following information is required:

- Organization ID
- Client ID (API Key)
- Client Secret

These can be stored in plaintext inside the config file:

```yaml
authentication_method: oauth
integration:
  org_id: "Organization ID goes here"
  client_id: "Client ID goes here"
  client_secret: "Client Secret goes here"
```

Replace each "goes here" string (including the double quotes) with the item
copied from the console.

# Credential Security

The `client_id` and `client_secret` are considered sensitive and should be
secured accordingly. If you intend to keep these items in plaintext, it is your
responsibility to restrict access to `connector-umapi.yml` using any necessary
practices (ACLs, file permissons, etc).

Any sensitive credential can be stored in a secure OS keychain (such as Windows
Credential Manager). Each credential is identified by key name and account ID
(which is the `org_id` for UMAPI credentials). In `connector-umapi.yml`, the key
name is stored in the respective config option.

* `secure_client_id_key` - Key name of `client_id`
* `secure_client_secret_key` - Key name of `client_secret`

We strongly recommend securing your credentials in this manner. See [Security
Recommendations](security.md#secure-credential-storage) for more information.

---

[Previous Section](connect_okta.md)  \| [Next Section](sync_from_csv.md)
