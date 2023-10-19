---
layout: default
lang: en
title: Installation
nav_link: Installation
nav_level: 2
nav_order: 270
parent: success-guide
page_id: install-sync
---

# Installation

[Previous Section](identify_server.html) \| [Back to Contents](index.html) \| [Next Section](setup_config_files.html)

## Installation Procedure

1. Create a directory where the sync tool will run
    * Windows example: `C:\adobe_user_sync`
    * Linux example: `~/adobe_user_sync`
2. Get the [latest release](https://github.com/adobe-apiplatform/user-sync.py/releases/latest)
    * Binary downloads are found in the "Assets" box immediately below the release notes
    * Be sure to select the correct release for your platform - the naming convention is `user-sync-[VERSION][EDITION]-[PLATFORM]`.
      Windows releases are packaged in `.zip` format and Linux releases are packaged in `.tar.gz` format.
    * **NOTE:** Releases tagged with the `-noext` edition tag ship with [extension support](../user-manual/advanced_configuration.html#custom-attributes-and-mappings)
      disabled. Do not install this variant unless that restriction is desired.
3. Extract the UST archive to the directory created in step 1.
    * Windows filename: `user-sync.exe`
    * Linux filename: `user-sync`
4. Generate the example configuration files
    * From the command line, run the command `./user-sync example-config` in the sync tool directory created in step 1
    * The tool will prompt you to specify the filename of each file. Press Enter for each to accept the default filenames.
    * For additional example configuration files and CSV templates, download `examples.zip` or `examples.tar.gz` from the
      release asset list (see step 2)
5. Refer to the [User Manual](../user-manual) for full User Sync Tool documentation.

[Previous Section](identify_server.html) \| [Back to Contents](index.html) \| [Next Section](setup_config_files.html)
