---
layout: default
lang: en
nav_link: Upgrade Guide
nav_level: 2
nav_order: 340
---

# Upgrade Guide
{:."no_toc"}

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Previous Section](scheduling.md) \| [Back to Contents](index.md)

---

# Why Upgrade?

To ensure security and stability, the development team of the User Sync Tool does not support older versions of the Sync
Tool. We encourage every user of the tool check for [new releases](https://github.com/adobe-apiplatform/user-sync.py/releases/latest)
regularly and keep their User Sync Tool up-to-date.

Any User Sync Tool release prior to 2.6.0 is packaged as a [pex](https://github.com/pantsbuild/pex) file, which requires an
external Python interpreter to run. To maximize compatibility, builds were targeted to Python 2.7 and Python 3.6 (or below).
Starting with 2.6.0, the sync tool is built and distributed as a self-contained executable. This executable embeds its own
Python environment, removing the requirement of an external Python interpreter.

This build model also makes it possible for the UST to be built with newer versions of Python. The executable build currently
runs with Python 3.9 (as of version 2.6.5). Older versions of Python are either no longer maintained, or are
[nearing end-of-life](https://endoflife.date/python).

The User Sync Tool also has many new features unavailable in older versions.

* Instant access to documentation - `./user-sync docs`
* Security key generation - `./user-sync certgen`
* Private key encryption and decryption - `./user-sync encrypt` and `./user-sync decrypt`
* Template config generation - `./user-sync example-config`
* LDAP Kerberos Support
* Admin Console identity connector
* Adobe Sign Sync capability

# Basic Procedure
