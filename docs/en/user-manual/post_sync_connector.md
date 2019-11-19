---
layout: default
lang: en
nav_link: Post-Sync Connector
nav_level: 2
nav_order: 70
---

# Post-Sync Connector

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Previous Section](advanced_configuration.md)  \| [Next Section](deployment_best_practices.md)

---

The Post-Sync Connector framework for the User Sync Tool performs optional sync
workflows with specific Adobe products. These workflows execute after the main
sync workflow completes.

Specific functionality depends on the connector(s) used.

Multiple connectors can be enabled and configured for a single sync process.

## Supported Connectors

NOTE: **Adobe Sign Sync** is currently the only supported connector.  Additional connectors will be released in the future.

| Connector | ID | Config File | Notes |
|---|---|---|---|
| Adobe Sign Sync | `sign` | `connector-sign-sync.yml` | See [Sign Sync Docs](#sign-sync-connector) below |
{: .bordertablestyle }

## Configuration

Each post-sync connector has its own configuration file to specify any configuration options needed by that connector.

Post-sync connectors are enabled in `user-sync-config.yml` with the optional `post-sync` config option.

Example:

```yaml
# user-sync-config.yml
post_sync:
  modules:
    - sign_sync
  connectors:
    sign_sync: connector-sign-sync.yml
```

This example shows the **Adobe Sign Sync** connector enabled.  The `modules` option specifies that the `sign_sync`
connector is enabled. `connectors.sign_sync` points the Sync Tool to the Sign connector config file, which tells
the Sign connector how to operate. After the main sync completes, the Sign connector will be executed.

**Config Spec**

| key | parent | type | notes |
|---|---|---|---|
| `post_sync` | n/a | `dict(str, mixed)` | Top-level config key that specifies which modules are enabled and where their configuration files live |
| `modules` | `post_sync` | `list(str)` | List of post-sync modules to enable. Connectors will be run in order specified |
| `connectors` | `post_sync` | `dict(str, str)` | Connector config files. Key: connector module; value: path to config file |
{: .bordertablestyle }

## Workflow

Post-sync connectors are executed after the main sync process completes. In the course of the sync process,
the Post-Sync Manager marshals the following data to be used be each post-sync connector.

* Identity source data, including any additional attributes
* The current state of all users in the Admin Console after the completion of the sync process (with respect to `--adobe-users`
  and any exclusion rules that may be specified)

This post-sync data is provided to each post-sync connector for post-sync execution. It will not be altered by any post-sync
connector.

During post-sync execution, each post-sync connector will be run in the order defined in `post_sync.modules`.

# Sign Sync Connector

The **Adobe Sign Sync** connector introduces an optional sync workflow to manage Adobe Sign users.

* Assign Sign users to specific Sign groups
* Define Group Admin and Account Admin role assignmet rules

## Native Sign &lt;-&gt; Admin Console Connection

The Adobe Sign Sync connector is not required to provision users to Adobe Sign. Users assigned to Sign Enterprise plans
are automatically granted basic Sign accounts when they are first provisioned to a Sign product profile in the
Admin Console. When Sign users are created in this manner, they are assigned to the **Default Group** in Sign
and are assigned **Normal User** privileges.

Taking advantage of this native sync functionality with the User Sync Tool is easy - just target an Adobe Sign
product profile in your group mapping in `user-sync-config.yml`.

```yaml
directory_users:
  groups:
    - directory_group: adobe-sign-enterprise
      adobe_groups:
        - Adobe Sign
```

Updates to user information (First Name, Last Name, and email address) are automatically synced to Sign
the next time the user logs into Sign.

## Feature Overview


| Feature | Notes |
|---|---|
| Sign group assignment | Assign Sign users to a non-default group |
| Admin Roles | Provision users in Sign with Group Admin or Account Admin privileges |
| Automatic group creation | Sign groups are created automatically if they don't already exist |
| Console-driven provisioning | Group and role assignment is governed by Admin Console group membership and/or Console admin role assignment |
{: .bordertablestyle }

## Configuration Overview

The Adobe Sign Sync configuration file, `connector-sign-sync.yml`, defines the behavior of the Adobe Sign sync process.

### Example

```yaml
# connector-sign-sync.yml
sign_orgs:
  - host: api.echosign.com
    key: [API key]
    admin_email: signadmin@example.com

user_groups:
  - Sign Users
  - More Sign Users

entitlement_groups:
  - Adobe Sign

identity_types:
  - federatedID

admin_roles:
  - sign_role: ACCOUNT_ADMIN
    adobe_groups:
      - Adobe Sign Account Admins
  - sign_role: GROUP_ADMIN
    adobe_groups:
      - Adobe Sign Group Admins
```

### Config Spec

| key | type | required? | notes |
|---|---|---|---|
| `sign_orgs` | `list(dict)` | Y | List of objects defining which Sign orgs to sync. If targeting a "secondary" org, it must be defined in `user-sync-config.yml` (see [docs](advanced_configuration.html#accessing-users-in-other-organizations)) |
| `user_groups` | `list(str)` | N | List of Adobe group names to potentially assign to a user in Sign. If a user belongs to any group in this list, they will be assigned to the first matching group in Sign (with respect to the order these groups are defined in the Sign config) |
| `entitlement_groups` | `list(str)` | Y | List of Adobe groups and/or product profiles that provision a user to Adobe Sign. Only users assigned to these groups will be processed by the Sign Sync connector. |
| `identity_types` | `list(enum)` | N | Identity types to be processed by Sign Sync connector.  Users of any type not specified here will not be processed. |
| `admin_roles` | `list(dict)` | N | List of mappings that define which Console user groups and/or admin roles determine Sign admin privileges |
{: .bordertablestyle }

### `sign_orgs` Spec

Each object defined in `sign_orgs` represents a connection to a different Sign organization. There should, at minimum, be one
Sign connection defined here - the connection to the Sign org that is linked to the "primary" UMAPI connection as defined in
`connector-umapi.yml`. Secondary Sign orgs can be defined here as well as long as their linked UMAPI connections are defined in
`user-sync-config.yml` (see [docs](advanced_configuration.html#accessing-users-in-other-organizations)).

| key | type | notes |
|---|---|---|
| `host` | `str` | Base Sign endpoint host (e.g. api.echosign.com); actual API hostname and endpoint will be resolved dynamically |
| `key` | `str` | API integration key |
| `admin_email` | `str` | Email address of Sign admin user associated with API key. This setting prevents the Sign Sync connector from performing any actions on this account |
| `console_org` | `str` | (only defined for secondary Sign conncections) Name of secondary Sign connection (must match any secondary UMAPI connection defined in `user-sync-config.yml`) |
{: .bordertablestyle }

### `admin_roles` Spec

`admin_roles` defines a list of zero or more group mappings that specify how user groups, product profiles, or Console admin roles
should define Sign admin role privileges.

Two types of Sign admin privileges can be assigned: `ACCOUNT_ADMIN` and `GROUP_ADMIN`.

`ACCOUNT_ADMIN` users have admin privileges for the entire Sign account (e.g. the Sign 'organization' linked to the Admin Console
organization).

`GROUP_ADMIN` users have admin privileges for the group they are assigned according to `user_groups`.

| key | type | notes |
|---|---|---|
| `sign_role` | `enum(str)` | Sign admin role to assign.  Valid values are `ACCOUNT_ADMIN` and `GROUP_ADMIN` |
| `adobe_groups` | `list(str)` | List of Adobe groups that grant the defined Sign admin privilege.  Any user that is a member of any group in this list will be assigned the defined privilege |
{: .bordertablestyle }

### Valid `identity_types` values

The `identity_types` option will limit the scope of the Sign sync connector by identity type.

The following types are valid:

* `adobeID`
* `enterpriseID`
* `federatedID`

If `identity_types` is not specified, then there will be no restrictions by identity type.

