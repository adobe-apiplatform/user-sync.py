---
layout: default
lang: en
nav_link: Connect to Adobe
nav_level: 2
nav_order: 31
parent: user-manual
page_id: connect-adobe
---

[Previous Section](configuring_user_sync_tool.md)  \| [Next Section](command_parameters.md)

# Connecting To Adobe
{:."no_toc"}

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

## Configuring a UMAPI Connection

All UMAPI sync setups require at least one UMAPI connector configuration. This primary connection config should
be called `connector-umapi.yml`.

This section focuses on a single connection. See the [advanced config](advanced_configuration.md#accessing-groups-in-other-organizations)
section for details around synchronizing to multiple UMAPI targets.

`connector-umapi.yml` defines two primary top-level config keys.

* `server` - Override default identity and UMAPI endpoints (generally not needed) and customize connection timeout and retry settings
* `enterprise` - Define UMAPI credentials (either in-line plaintext or references to OS keyring objects)

## `server` Settings

The `server` settings do not generally need to be customized. `timeout` and `retry` settings can be customized if the Sync Tool
is running on a high-latency network connection.

## `enterprise` Settings

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
  priv_key_path: "Path to Private Certificate goes here" (default: private.key)
```

Replace each "goes here" string (including the double quotes) with the item copied from the console. If `private.key` is
placed in the same directory as `connector-umapi.yml`, then `priv_key_path` can be relative.

`enterprise` supports additional advanced configuration options. Some of those are covered in [Advanced Configuration](advanced_configuration.md)
and all are documented in the example configuration file.

## Credential Security

The `client_secret` and the contents of `private.key` are considered sensitive and should be secured accordingly. If
you intend to keep these items in plaintext, it is your responsibility to restrict access to `connector-umapi.yml`
and `private.key` using any necessary practices (ACLs, file permissons, etc).

We strongly recommend using the OS keychain to store sensitive credentials. See [Security Recommendations](deployment_best_practices.md#security-recommendations) for more information.

---

[Previous Section](configuring_user_sync_tool.md)  \| [Next Section](command_parameters.md)
