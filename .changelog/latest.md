# Features

* 8c4ea5c Implement username update (disabled by default - see #819)
* #819 Add `update_attributes` config to govern which user attributes can be updated
  * `username` disabled by default, all others enabled
  * Generates warning message when a disabled attribute is different (assuming `--update-user-info` is enabled)
* [OAuth Server-to-Server Support](https://developer.adobe.com/developer-console/docs/guides/authentication/ServerToServerAuthentication/implementation/)
  * New config option in UMAPI connector config and Admin Console connector:
    `authentication_method`
  * Set to `oauth` to enable Server-to-Server support
  * Server-to-Server auth only requires Client ID and Client Secret
  * JWT authentication is deprecated and will be removed in a future version
  * More information
    * https://github.com/adobe-apiplatform/user-sync.py/blob/user-guide-wip/en/user-manual/connect_adobe.md
    * https://github.com/adobe-apiplatform/user-sync.py/blob/user-guide-wip/en/user-manual/sync_from_console.md

# Fixes

* #811 Fix user email update failures

# Build Changes

* Github Actions no longer maintains a build for Ubuntu Bionic (18.04),
  so automated `bionic` builds are no longer available. Automated builds
  for 22.04 Jammy have been added with the `jammy` label.

# Advisory

This is a pre-release and may not be stable for production use. The username
update feature is under development and will currently update the username of
any user that can be identified as being in need of a username update. This
may have unexpected side effects.
