# New Features

**Revamped Sign Sync**

Sign Sync has been overhauled. It is now implemented as a separate workflow with an alternate entrypoint command (`sign-sync`).

Feature summary

- Primary config for Sign Sync is `sign-sync-config.yml`
- Sign connector config - `connector-sign.yml`
- All identity sources are supported
- Sync supports multiple Sign targets
- Full user lifecycle management for standalone Sign environments
- Mapping structure to manage Sign group assignments and admin privileges
- Same logging options as UMAPI sync

Architecture changes

- New `engine` module
- `rules.py` refactored to `engine.umapi`
- `config.py` refctored to multi-file module
- Sign API client is top-level (parallel to `user_sync` module)
- `post_sync` has been removed

Notes:

- User multi-group (UMG) is not supported at this time
- The Sign client uses Sign API v5

Documentation is forthcoming.
