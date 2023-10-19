---
layout: default
lang: en
title: Connect to Adobe
nav_link: Connect to Adobe
nav_level: 2
nav_order: 41
parent: user-manual
page_id: connect-adobe
---

[Previous Section](runtime_config.html)  \| [Next Section](connect_ldap.html)

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

All UMAPI sync setups require at least one UMAPI connector configuration. This
primary connection config should be called `connector-umapi.yml`.

This section focuses on a single connection. See the [advanced
config](advanced_configuration.html#accessing-groups-in-other-organizations)
section for details around synchronizing to multiple UMAPI targets.

Before configuring any UMAPI connections, you must set up an integration for
each target. See the [Setup and
Installation](setup_and_installation.html#adobe-developer-console-setup) page for
more information.

`connector-umapi.yml` defines three top-level config keys.

* `authentication_method` - Tells the UMAPI connector to use Server-to-Server
  authentication or deprecated JWT authentication
* `server` - Override default identity and UMAPI endpoints (generally not
  needed) and customize connection timeout and retry settings
* `enterprise` - Define UMAPI credentials (either in-line plaintext or
  references to OS keyring objects)

# General Settings

## `authentication_method`

`authentication_method` governs the type of authentication to use when
communicating with the UMAPI. Two options are supported.

- `oauth` (**recommended**) - Use OAuth Server-to-Server authentication. This is
  simple to set up and unlike JWT does not require a certificate pair. See
  [Setup and
  Installation](setup_and_installation.html#adobe-developer-console-setup) for
  more info.
- `jwt` - This is the default for compatibility reasons, but should generally
  not be used because JWT authentication is deprecated.

## `ssl_verify`

The `ssl_verify` setting should be used as a last resort to make the User Sync
Tool work in environments where it can't connect to Adobe services.
Specifically, it can be used in cases where the UST reports SSL errors like this
when running.

```
UMAPI connection to org id failed: [SSL: CERTIFICATE_VERIFY_FAILED]
```

Please note this option isn't recommended and should only be used when [other
options](security.html#dealing-with-ssl-issues) have been exhausted.

# `server` Settings

The `server` settings do not generally need to be customized. `timeout` and
`retry` settings can be customized if the Sync Tool is running on a high-latency
network connection.

> **Note:** The options `ims_host` and `ims_endpoint_jwt` are deprecated in
> favor of the options `auth_host` and `auth_endpoint`. These options serve the
> same purpose as their deprecated counterparts.

# `enterprise` Settings

The `enterprise` key defines credentials used to authenticate with the User
Management API. The set of fields required to configure the connection vary
depending on `authentication_method`.

## `oauth` Authentication

`oauth` Server-to-Server authentication requires the following fields to be
configured under the `enterprise` key. These items can be found on the
credentials page of your UMAPI project in the [Developer
Console](https://developer.adobe.com/console).

- `org_id` - Organization ID
- `client_id` - Unique client identifier
- `client_secret` - Secret token used to authenticate with the User Management
  API

Example:

```yaml
authentication_method: oauth

enterprise:
  org_id: "12345@AdobeOrg"
  client_id: "12345-abc-9876"
  client_secret: "9876-xyz-12345"
```

These fields can be stored in plaintext inside the config file, but if you do
that be sure to keep the file secure. Client ID and Client Secret are considered
sensitive. It is also possible to store these items securely. See [Credential
Security](#credential-security) for more information.

## `jwt` Authentication (deprecated)

> **WARNING:** JWT authentication is deprecated and support is set to be dropped
> at the end of 2024. Please plan accordingly and migrate any existing JWT
> integrations to Server-to-Server.

The following fields are required.

- `org_id` - Organization ID
- `client_id` - Client ID (API Key)
- `client_secret` - Secret token for API client
- `tech_acct_id` - Username of the technical account associated with the
  integration
- `priv_key_path` - Path to the private key associated with the public key that
  was provided to the developer console when setting up the integration

All items except for the key file (`private.key`) can be found on the [Adobe
Developer Console](https://developer.adobe.com/console/). The `private.key` file
should already be present on the server that will be running the User Sync Tool.
It is the private key associated with the pulic key that was used to create the
UMAPI integration.

These can be stored in plaintext inside the config file:

```yaml
authentication_method: jwt

enterprise:
  org_id: "Organization ID goes here"
  client_id: "Client ID goes here"
  client_secret: "Client Secret goes here"
  tech_acct_id: "Tech Account ID goes here"
  priv_key_path: "private.key"
```

Replace each "goes here" string (including the double quotes) with the item
copied from the console. If `private.key` is placed in the same directory as
`connector-umapi.yml`, then `priv_key_path` can be relative.

> If storing sensitive items (client ID, client secret and private key) in
> plaintext, be sure to set file permissions and/or ACLs to limit access to
> these files. It is also possible to store these items securely. See
> [Credential Security](#credential-security) for more information.

### Private Key Settings

The private key file can optionally be stored differently than a plain file
referenced by `priv_key_path`.

* The key's contents can be stored inside the config file using the
  `priv_key_data` option. Note that this must be the raw, unencrypted contents
  of `private.key`.

  ```yaml
  priv_key_data: |
     -----BEGIN RSA PRIVATE KEY-----
     MIIf74jfd84oAgEA6brj4uZ2f1Nkf84j843jfjjJGHYJ8756GHHGGz7jLyZWSscH
     [....]
     CoifurKJY763GHKL98mJGYxWSBvhlWskdjdatagoeshere986fKFUNGd74kdfuEH
     -----END RSA PRIVATE KEY-----
  ```

* The private key file can also be symmetrically encrypted. This type of
  encryption uses a passphrase to secure secure the file. The passphrase can be
  specified in `priv_key_pass`. If the passphrase option is set, then
  `priv_key_path` should contain the path to the encrypted key file.
  
  To encrypt the private key file, use the `encrypt` command:
  
  ```
  $ ./user-sync encrypt
  ```
  
  If invoked with no additional options, `encrypt` will prompt you for a
  passphrase and then encrypt `private.key`, replacing the plaintext file with
  the encrypted version.
  
  See [here](additional_tools.html#private-key-encryption) for full details.

# Migrating From JWT to Server-to-Server

Migrating from JWT to Server-to-Server is a simple process. Use this guide if
you already use the User Sync Tool and wish to migrated from JWT to
Server-to-Server.

This guide applies to a single UMAPI integration / Admin Console target. If your
sync is configured to manage multiple targets, then repeat this process for
every UMAPI target.

1. Open the project in the [Developer
   Console](https://developer.adobe.com/console) associated with your UMAPI
   integration. If you open the credential page, you will be prompted to begin
   the credential migration process. Refer to [this
   document](https://developer.adobe.com/developer-console/docs/guides/authentication/ServerToServerAuthentication/migration/)
   for a step-by-step guide for migrating. Return to this guide when the
   migration guide advises you to test your application.
2. Make note of the new credentials page. Your UMAPI connector config file
   will already contain the credentials you need - `org_id`, `client_id` and
   `client_secret`.
3. Edit your UMAPI config file (i.e. `connector-umapi.yml`) with the these
   changes
   * Add top-level `authentication_method` key (if one doesn't exist) and set
     the value to `oauth`
   * Under `enterprise`, remove `tech_acct_id` and `priv_key_path` items
   * If you are using credential storage, then instead remove config related to
     the private key - key contents, encrypted file passphrase etc (in addition
     to tech acct ID).
   * Your config should look something like this:

   ```yaml
    authentication_method: oauth

    enterprise:
      org_id: "Org ID goes here"
      client_id: "Client ID goes here"
      client_secret: "Client secret goes here"
   ```
4. Run UST in test mode. You should get no errors regarding UMAPI connectivity.
5. If everything looks good, then complete the migration as per the migration
   guide. Your old JWT credentials will be deleted.
6. Delete your private key and remove anything in credential storage related to
   it.

# Credential Security

The `client_id`, `client_secret` and the contents of `private.key` are
considered sensitive and should be secured accordingly. If you intend to keep
these items in plaintext, it is your responsibility to restrict access to
`connector-umapi.yml` and `private.key` using any necessary practices (ACLs,
file permissons, etc).

Any sensitive credential can be stored in a secure OS keychain (such as Windows
Credential Manager). Each credential is identified by key name and account ID
(which is the `org_id` for UMAPI credentials). In `connector-umapi.yml`, the key
name is stored in the respective config option.

* `secure_client_id_key` - Key name of `client_id`
* `secure_client_secret_key` - Key name of `client_secret`
* `secure_priv_key_data` - Key name of `priv_key_data`**\***
* `secure_priv_key_pass_key` - Key name of `priv_key_pass`

> **\*** Some keyring backends such as Windows Credential Manager impose a
> character limit on the password field. This makes it impossible to store the
> private key contents. We recommend instead to encrypt the key file and
> securely store the private key passphrase.

We strongly recommend securing your credentials in this manner. See [Security
Recommendations](security.html#secure-credential-storage) for more information.

---

[Previous Section](runtime_config.html)  \| [Next Section](connect_ldap.html)
