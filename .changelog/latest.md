# Fixes

* #825 send `start_sync()` signal when querying groups for auto-create purposes
* #834 make TimeoutException a child of AssertionException so we don't show a stack trace
* #837 fix typo in sign engine log message
* #840 push strategy fails with unhandled exception
* e61ec81 Fix issue with all users setting

# New Features

* 5e9e01b Ability to exclude Sign users in Sign Sync
* d761c5e Introduce option to limit scope of Adobe-only users to just those that have groups to remove in the current sync. See [the manual](https://github.com/adobe-apiplatform/user-sync.py/blob/8082c987c79eddcc3fc06f31a1c32de300a30cd7/en/user-manual/configuring_user_sync_tool.md#limits-config) for more information
