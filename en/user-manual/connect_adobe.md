---
layout: default
lang: en
title: Connect to Adobe
nav_link: Connect to Adobe
nav_level: 2
nav_order: 31
parent: user-manual
page_id: connect-adobe
---

[Previous Section](configuring_user_sync_tool.md)  \| [Next Section](connect_ldap.md)

# Connecting To Adobe
{:."no_toc"}

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# Configuring a UMAPI Connection

All UMAPI sync setups require at least one UMAPI connector configuration. This primary connection config should
be called `connector-umapi.yml`.

This section focuses on a single connection. See the [advanced config](advanced_configuration.md#accessing-groups-in-other-organizations)
section for details around synchronizing to multiple UMAPI targets.

`connector-umapi.yml` defines two primary top-level config keys.

* `server` - Override default identity and UMAPI endpoints (generally not needed) and customize connection timeout and retry settings
* `enterprise` - Define UMAPI credentials (either in-line plaintext or references to OS keyring objects)

# `server` Settings

The `server` settings do not generally need to be customized. `timeout` and `retry` settings can be customized if the Sync Tool
is running on a high-latency network connection.

# `enterprise` Settings

The `enterprise` key defines credentials used to authenticate with the User Management API. The following information
is required:

- Organization ID
- Client ID (API Key)
- Client Secret
- Technical Account ID
- Private Key File Path

All items except for the key file (`private.key`) can be found on the [Adobe Developer Console](https://developer.adobe.com/console/).
The `private.key` file should already be present on the server that will be running the User Sync Tool.

These can be stored in plaintext inside the config file:

```yaml
enterprise:
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
  $ ./user-sync encrypt
  ```
  
  If invoked with no additional options, `encrypt` will prompt you for a passphrase and then encrypt `private.key`,
  replacing the plaintext file with the encrypted version.
  
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

[Previous Section](configuring_user_sync_tool.md)  \| [Next Section](connect_ldap.md)
