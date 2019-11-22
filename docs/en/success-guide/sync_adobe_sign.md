---
layout: default
lang: en
nav_link: Adobe Sign Sync
nav_level: 2
nav_order: 330
---

# Adobe Sign Sync Guide
{:."no_toc"}

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Previous Section](scheduling.md) \| [Back to Contents](index.md)

---

# Getting Started

**NOTE:** The Adobe Sign Sync Connector is not required to provision users to Adobe Sign. It provides optional advanced functionality.
See the [User Manual page](../user-manual/post_sync_connector.html#native-sign---admin-console-connection) for more details.

This guide assumes that the User Sync Tool is set up and configured to sync users from an existing identity source.

## Set Up Sign Integration

The connector talks directly to Adobe Sign using the Sign API.  In order to use the connector, it is necessary to create a Sign API
integration key.

**NOTE:** You must be logged in as an administrator to create a new integration key

1. Log into Adobe Sign
2. Click "Accout" on the top navigation bar
3. On the left-hand menu, click "Adobe Sign API"
4. On the "API Information" page, find the "Integration Key" link

   ![](images/sign_sync/sign_api_info.png)

   If you don't see this link, please contact Sign support
5. On the "Create Integration Key" page, give the integration a name and select the `user_read` and `user_write` scopes
6. Save the integration
7. On the "Access Tokens" list, select the integration you just created
8. Click "Integration Key" to display the integration key.  This is used in the Sign Sync connector config file.

   ![](images/sign_sync/sign_key_display.png)

## Generate the Connector Config

Open a command line terminal and change working directory to the directory containing the User Sync Tool.

```sh
$ ./user-sync example-config-sign
# enter filename or press Enter to accept the default (connector-sign-sync.yml)
Sign Sync Config Filename [connector-sign-sync.yml]: connector-sign-sync.yml
Generating file 'connector-sign-sync.yml'
```

This creates a template Sign Sync connector config file in your current working directory.

## Configure Post-Sync

Open `user-sync-config.yml` in a text editor and add the following:

```yaml
# "post_sync" is a root key and should be specified at the top-level of
# the file (alongside directory_users, adobe_users, etc)
post_sync:
  modules:
    - sign_sync
  connectors:
    sign_sync: connector-sign-sync.yml
```

This assumes your Sign Sync connector config file is named `connector-sign-sync.yml`. Change the filename if needed.

Post-sync is now configured. Future post-sync connectors can be enabled here.

## Specify Sign Group Mapping

If your existing User Sync config does not assign Adobe Sign entitlements, it will be necessary to add a group mapping that
targets Adobe Sign.

This example assumes that there is a Sign product profile on the target Admin Console called `Adobe Sign`. Change the target
Adobe group to reflect the name of the desired target product profile. You can also target a user group that is associated with
a Sign product profile.

It also assumes there is a directory group in the identity source called `adobe-sign-enterprise`. Change the directory group name
to reflect the desired group name.

```yaml
directory_users:
  # ... other directory_users settings
  groups:
    # ... other group mappings
    - directory_group: adobe-sign-enterprise
      adobe_groups:
        - Adobe Sign
```

As with any other group mapping, the users belonging to `adobe-sign-enterprise` will be synced to the Admin Console and
assigned to the `Adobe Sign` group. Users assigned to a Sign profile or associated user group will automatically
be synced to Adobe Sign.

Additional group mappings are required to take advantage of Sign group and admin role assignment. Those are covered in
[Managing Group Assignments](#managing-group-assignments) and [Managing Admin Role Assignments](#managing-admin-role-assignments).

## Basic Sign Config

The file `connector-sign-sync.yml` generated previously contains a template for a basic Sign Sync connector config. The next step
is to set up a basic configuration by providing the Sign API connection details and telling the connector which group(s) are
resonsible for entitling Sign users.

Open `connector-sign-sync.yml` config file in a text editor.

### Define the Console Org

The top of the file will specify the Sign org(s) for the connector to sync.

```yaml
sign_orgs:
  - console_org:
    host: api.echosign.com
    key: (integration key)
    admin_email: (email address of account associated with the API key)
```

Edit this section to configure the Sign API connection.

1. `console_org` can be left blank.
2. `host` should be set to api.echosign.com
3. `key` is the API key [generated previously](#set-up-sign-integration)
4. `admin_email` is the email address associated with the API key. This prevents the Sign Sync connector from operating on this user
   and potentially changing its admin role status.

### Define Entitlement Groups

Finally, modify the `entitlement_groups` list to reflect the group or groups that entitle a user to Adobe Sign access. This will be the
same Sign group or groups that you defined in your UST group mapping previously. Following the previous example, we will want to put
`Adobe Sign` as the sole group.

```yaml
entitlement_groups:
  - Adobe Sign
```

This config option helps to define the scope of which users should be processed by the Sign Sync connector. It ensures that users
without Sign access will not be processed.

### (Optional) Define Identity Types

If the UST has been configured to handle Adobe IDs and/or Enterprise IDs, the `identity_types` key should be set to handle the same
identity types.

For example, this is what it would look like if the UST is managing `federatedID` and `enterpriseID` users:

```yaml
identity_types:
  - enterpriseID
  - federatedID
```

This tells the Sign Sync connector to only operate on `federatedID` and `enterpriseID` users and to ignore `adobeID` users.

### Test the Connector

The connector won't really do anything useful at this point, but it is a good idea to test it now to make sure the Sign API
connection works as expected.

**NOTE:** The Sign API does not have a "test mode" like the User Management API has. To prevent unexpected sync behavior,
the Sign Sync connector is disabled when the UST is run in test mode. You may want to temporarily disable non-Sign-related
group mappings in `user-sync-config.yml` to prevent non-Sign users from getting synced during this test.

Open a command-line terminal, change your working directory to where the UST is installed, and run the sync command typical
for your sync setup.

Example:

```sh
$ ./user-sync --process-groups --users mapped
```

# Managing Group Assignments

# Managing Admin Role Assignments
