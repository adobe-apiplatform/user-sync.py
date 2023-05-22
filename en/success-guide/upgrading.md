---
layout: default
lang: en
title: Upgrade Guide
nav_link: Upgrade Guide
nav_level: 2
nav_order: 340
parent: success-guide
page_id: upgrade-guide
---

# Upgrade From PEX to Binary
{:."no_toc"}

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Previous Section](scheduling.md) \| [Back to Contents](index.md)

---

# Why Upgrade?

To ensure security and stability, the development team of the User Sync Tool
does not support older versions of the Sync Tool. We encourage every user of the
tool check for [new
releases](https://github.com/adobe-apiplatform/user-sync.py/releases/latest)
regularly and keep their User Sync Tool up-to-date.

Any User Sync Tool release prior to 2.6.0 is packaged as a
[pex](https://github.com/pantsbuild/pex) file, which requires an external Python
interpreter to run. To maximize compatibility, builds were targeted to Python
2.7 and Python 3.6 (or below). Starting with 2.6.0, the sync tool is built and
distributed as a self-contained binary executable. This executable embeds its
own Python environment, removing the requirement of an external Python
interpreter.

This build model also makes it possible for the UST to be built with newer
versions of Python. The executable build currently runs with Python 3.9 (as of
version 2.6.5). Older versions of Python are either no longer maintained, or are
[nearing end-of-life](https://endoflife.date/python).

The User Sync Tool also has many new features unavailable in older versions.

* Instant access to documentation - `./user-sync docs`
* Security key generation - `./user-sync certgen`
* Private key encryption and decryption - `./user-sync encrypt` and `./user-sync decrypt`
* Template config generation - `./user-sync example-config`
* LDAP Kerberos Support
* Admin Console identity connector
* Adobe Sign Sync capability
* See the [changelog](https://raw.githubusercontent.com/adobe-apiplatform/user-sync.py/v2/.changelog/changelog.md) for more details

# Compatibility

The binary build of the UST has been tested on the supported versions of our
targeted platforms (Windows, CentOS and Ubuntu). It is compatible with most
major versions except for older Ubuntu LTS releases.

The UST development team generally targets the environments supported by Github Actions.

[https://github.com/actions/runner-images](https://github.com/actions/runner-images)

With the exception of macOS, which currently isn't supported, and CentOS, which
is supported for certain versions.

Newer Ubuntu builds of the tool are unlikely to be combatible with older
releases due to system library changes. It may be possible to upgrade libc and
other system packages to get the tool running, but the UST development team will
not be able to provide support.

The tool can also be built from source to run on unsupported platforms. See the
[build
instructions](https://github.com/adobe-apiplatform/user-sync.py#build-instructions)
in the readme. Note that Python 3.9 is required to build the tool, which may
need to be installed on the system (or built from source).



| Platform | Compatible? | Notes |
|---|---|---|
| Windows Server 2012R2 | ? | We can't guarantee 2012R2 compatibility. Use at your own risk. |
| Windows Server 2016 | ? | The sync tool should likely work with 2016, but we can't guarantee it. |
| Windows Server 2019 | Y | |
| Windows Server 2022 | Y | |
| CentOS/RedHat Enterprise Linux 7 | Y | |
| CentOS/RedHat Enterprise Linux 8 | Y | |
| Ubuntu Trusty 12.04 | N | |
| Ubuntu Xenial 16.04 | N | |
| Ubuntu Bionic 18.04 | N | Bionic is no longer supported as of `v2.9.0` |
| Ubuntu Focal 20.04 | Y | Use `ubuntu-focal` build |
| Ubuntu Jammy 22.04 | Y | Use `ubuntu-jammy` build |
{: .bordertablestyle }

# Basic Procedure

**Note:** If you run multiple sync processes (perhaps to sync from different
identity sources), we recommend repeating this procedure for each sync config.
You will not need to repeat steps 1 and 2 if each sync is run from the same root
directory.

1. Download the [latest release](https://github.com/adobe-apiplatform/user-sync.py/releases/latest) for your platform.
2. Extract the release archive and copy the `user-sync` (or `user-sync.exe`)
   binary to the system's sync tool directory.
3. Run the sync tool in test mode.
    1. Open command-line terminal
    2. `cd /path/to/ust`
    3. Run the command you would use to make a live sync, but running the UST
       executable and appending the `-t` command-line option
        
       This is the command you would run from the cron job/scheduled task, or
       the associated shell script/batch file

       **Linux example** -- if the command to run the tool in live mode is
       `python user-sync.pex --process-groups --users mapped` then the command
       to test the new binary version is `./user-sync --process-groups --users
       mapped -t`

       **Windows example** -- using the pex-based command in the Linux example,
       the command to test the Windows EXE is `.\user-sync.exe --process-groups
       --users mapped -t`
4. Compare log output from test run to log output from previous live run.
   
   There isn't an exact procedure we can outline here -- each UST installation
   is different. In general, look at the counts in the sync summary and make
   sure they aren't radically different. Look at the log messages for any errors
   or anomalous behavior.

   Note that log messages in the test run may be worded differently or may
   appear in a different order.

   If you need help, please [reach out](#getting-help).

5. IF the test logs look good, update the sync command in the cron job/scheduled
   task or associated script.

   Use the same command you used to test the file with the test mode flag (`-t`)
   removed.

   Check the UST logs after the next time it runs to ensure it behaves as
   expected.

# Getting Help

Please [create an
issue](https://github.com/adobe-apiplatform/user-sync.py/issues) if you need
help with the upgrade process.

[Previous Section](scheduling.md) \| [Back to Contents](index.md)
