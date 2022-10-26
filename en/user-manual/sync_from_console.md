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

The User Sync Tool can use the Admin Console as an identity connector. This can be used to manage users
for a trustee directory when the parent directory uses Azure AD sync or Google Sync, or to manage
[Sign Enterprise Users](sign_sync.md#sign-enterprise).

# Initial Setup

The connector can be enabled by adding `adobe_console` to `directory_users.connectors` in `user-sync-config.yml`.

```yaml
directory_users:
  connectors:
    adobe_console: connector-adobe-console.yml
```

A template config file can be obtained [here](https://github.com/adobe-apiplatform/user-sync.py/blob/v2/examples/config%20files%20-%20basic/connector-adobe-console.yml).

To invoke the sync tool with the `adobe_console` connector, do one of the following.

* Specify `adobe_console` as the `connector` in `invocation_options` inside `user-sync-config.yml`.

  ```yaml
  invocation_options:
    connector: adobe_console
  ```
* Run the Sync Tool with the option `--connector adobe_console`

  ```
  $ ./user-sync --connector adobe_console
  ```

# Configuring a Connection

All UMAPI sync setups require at least one UMAPI connector configuration. This primary connection config should
be called `connector-umapi.yml`.

Like the UMAPI connector, the Admin Console Connector requires a [service account integration on adobe.io](setup_and_installation.md##set-up-a-user-management-api-integration-on-adobe-io)

`connector-adobe-console.yml` defines three top-level config keys.

* `server` - Override default identity and UMAPI endpoints (generally not needed) and customize connection timeout and retry settings
* `integration` - Define UMAPI credentials (either in-line plaintext or references to OS keyring objects)
* `identity_type_filter` - Tells the connector to only include the identity type specified (`adobeID`, `enterpriseID` or
  `federatedID`)

## `server` Settings

The `server` settings do not generally need to be customized. `timeout` and `retry` settings can be customized if the Sync Tool
is running on a high-latency network connection.

## `integration` Settings

The `integration` key defines credentials used to authenticate with the User Management API. The following information
is required:

- Organization ID
- Client ID (API Key)
- Client Secret
- Technical Account ID
- Private Key File Path

All items except for the key file (`private.key`) can be found on the [Adobe Developer Console](https://developer.adobe.com/console/).
The `private.key` file should already be present on the server that will be running the User Sync Tool.

> **Note**: The default filename `private.key` is used here for the sake of clarity since it is the default filename
> when generating the certificate pair. In your UST setup, you will want to plan to change the filename (i.e. `src-private.key`)
> to distinguish it from the `private.key` file used for the UMAPI sync target. This page will continue to refer
> to it as `private.key`.

These can be stored in plaintext inside the config file:

```yaml
integration:
  org_id: "Organization ID goes here"
  client_id: "Client ID goes here"
  client_secret: "Client Secret goes here"
  tech_acct_id: "Tech Account ID goes here"
  priv_key_path: "private.key"
```

Replace each "goes here" string (including the double quotes) with the item copied from the console. If `private.key` is
placed in the same directory as `connector-umapi.yml`, then `priv_key_path` can be relative.

## Private Key Settings

The private key file can optionally be stored differently than a plain file referenced by `priv_key_path`.

* The key's contents can be stored inside the config file using the `priv_key_data` option. Note that this must be
  the raw, unencrypted contents of `private.key`.

  ```yaml
  priv_key_data: |
     -----BEGIN RSA PRIVATE KEY-----
     MIIf74jfd84oAgEA6brj4uZ2f1Nkf84j843jfjjJGHYJ8756GHHGGz7jLyZWSscH
	 [....]
     CoifurKJY763GHKL98mJGYxWSBvhlWskdjdatagoeshere986fKFUNGd74kdfuEH
     -----END RSA PRIVATE KEY-----
  ```

* The private key file can also be symmetrically encrypted. This type of encryption uses a passphrase to secure
  secure the file. The passphrase can be specified in `priv_key_pass`. If the passphrase option is set, then
  `priv_key_path` should contain the path to the encrypted key file.
  
  To encrypt the private key file, use the `encrypt` command:
  
  ```
  $ ./user-sync encrypt src-private.key
  ```
  
  If invoked in this manner, `encrypt` will prompt you for a passphrase and then encrypt `src-private.key`,
  replacing the plaintext file with the encrypted version. Replace `src-private.key` with the filename
  of your console connector key file.
  
  See [here](additional_tools.md#private-key-encryption) for full details.

# Credential Security

The `client_id`, `client_secret` and the contents of `private.key` are considered sensitive and should be secured accordingly.
If you intend to keep these items in plaintext, it is your responsibility to restrict access to `connector-umapi.yml`
and `private.key` using any necessary practices (ACLs, file permissons, etc).

Any sensitive credential can be stored in a secure OS keychain (such as Windows Credential Manager). Each credential
is identified by key name and account ID (which is the `org_id` for UMAPI credentials). In `connector-umapi.yml`, the key name
is stored in the respective config option.

* `secure_client_id_key` - Key name of `client_id`
* `secure_client_secret_key` - Key name of `client_secret`
* `secure_priv_key_data` - Key name of `priv_key_data`**\***
* `secure_priv_key_pass_key` - Key name of `priv_key_pass`

**\*** Some keyring backends such as Windows Credential Manager impose a character limit on the password field.
This makes it impossible to store the private key contents. We recommend instead to encrypt the key file
and securely store the private key passphrase.

We strongly recommend securing your credentials in this manner.
See [Security Recommendations](deployment_best_practices.md#security-recommendations) for more information.

---

[Previous Section](connect_okta.md)  \| [Next Section](sync_from_csv.md)
