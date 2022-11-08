---
layout: default
lang: en
title: Security
nav_link: Security
nav_level: 2
nav_order: 90
parent: user-manual
page_id: security
---

[Previous Section](additional_tools.md)  \| [Next Section](deployment_best_practices.md)

# Security
{:."no_toc"}

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# General Security Tips

The environment in which the User Sync Tool is run should be secured according
to industry best practices. The Sync Tool requires access to a number of
sensitive credentials in order to operate.

* User Management API
* LDAP
* Sign API
* etc

In addition, the tool deals with potentially sensitive information when
managing Adobe users.

* Email Address
* Username
* First Name
* Last Name

Such information can be stored in log files and is transmitted to and from Adobe
servers.

Tips:

* Run the User Sync Tool with a dedicated user account. This account should only
  be granted the permissions needed to run the tool.
* Ensure that file permissions/ACLs are set such that other non-admin system
  users cannot access UST configuration and log files.

# Secure Credential Storage

The User Sync Tool supports the secure storage of all sensitive credentials. It
relies on an operating system's secure keyring system to store sensitive
information, retrieving each item securely as needed.

Many storage types (backends) are supported, including:

| OS      | Systems Supported          |
|---------|----------------------------|
| Windows | Windows Credential Manager |
| Linux   | Freedesktop Secret Service |
| macOS   | macOS Keychain             |

> **Note**: Linux systems may need additional software installed, as keychain
> systems tend to require desktop environments in order to operate.

## How It Works

Here is a basic overview of the credential storage and retrieval process. We use
Windows screenshots to illustrate the process, but the same basic procedure
applies to any storage system. On Windows, the backend system used is Windows
Credential Manager, which can be found on any Windows system.

1. Create credential in keychain and set key name (internet name/address),
   username and password.

   ![](media/cred-create-generic.png)

   (in Windows Credential Manager, click "Add a generic credential")

2. Provide credential details and save credential.

   ![](media/cred-provide-details.png)

   These fields may be named differently depending on the system. In Windows,
   they map as follows:

   * **Internet or network address** - This can be any key name you wish to
     assign your credential e.g. `my_ust_ldap_password`.
   * **User name** - This varies depending on the configuration file. It should
     be the LDAP user for the LDAP config, org ID for UMAPI config, etc.
     Refer to the documentation for the configuration you're working with.
   * **Password** - This is the password you wish to store.

   The saved entry looks like this:

   ![](media/cred-saved.png)

3. Update your configuration file to use the stored credential.

   **Note**: Refer to the manual page for the configuration file you're working
   with to get exact details on how to modify your config.

   [LDAP config](connect_ldap.md#simple-auth) example:

   ```yaml
   secure_password_key: my_ldap_password
   # password:
   ```

# Network Environment

Some network configurations can cause problems for the User Sync Tool's ability
to connect to Adobe services such as the User Management API.

Connection problems can happen a variety of ways:

* Timeouts
* Connection errors
* SSL errors
* etc

## Hostname Allowances

The most reliable method for resolving connection issues is to ensure that any
firewall, proxy or other network security appliance is configured to allow
traffic to/from Adobe's services. Specifically, the hosts involved with the
User Sync Tool:

* `ims-na1.adobelogin.com`
* `usermanagement.adobe.io`
* `*.echosign.com`
* `*.adobesign.com`

These should ideally be added to an allowlist in any firewall, proxy system,
etc so they will implicitly trust these hosts and allow HTTPS calls to them.

> Adobe cannot provide server IP addresses or ranges because the IP address
> assigned any given server may change at any time.

## Proxies

The User Sync Tool can support certain network proxies. The UST uses the
`HTTPS_PROXY` environment variable when a proxy connection is needed. The
host or address specified in `HTTPS_PROXY` should be set to the proxy that the
UST should connect through.

Example:

```
# linux example
$ export HTTPS_PROXY="http://10.10.1.10:1080"

# windows cmd example
C:\> set HTTPS_PROXY="http://10.10.1.10:1080"

# powershell example
PS> $env:HTTPS_PROXY = "http://10.10.1.10:1080"
```

Accounts/passwords are supported with simple auth:

```
$ export HTTPS_PROXY="http://user:password@10.10.1.10:1080"
```

> **Note:** Securing the password in plaintext in an evironment variable in this
> manner is not recommended.

## Dealing with SSL Issues

SSL errors such as `CERTIFICATE_VERIFY_FAILED` are generally related to the
environment in which the User Sync Tool is running.

What we typically see are environments in which there is a proxy, firewall or
some other network security appliance which inspects outgoing SSL traffic but
doesn't re-encrypt it correctly. Or it could be the case there is some type of
"zero-trust" system in place that utilizes custom private client certificates.

Either way, the UMAPI and/or Sign client isn't able to communicate with the
Adobe service endpoints needed to conduct user sync.

The UST development team is unfortunately limited in our ability to support this
type of situation. Here are some possible solutions:

1. Point the UST/UMAPI client to the correct certificate bundle. See
   [here](https://helpx.adobe.com/enterprise/kb/UMAPI-UST.html#SSLCERTIFICATEVERIFYFAILED)
   for more information.

   **Note**: The Sign client uses a different underlying HTTP client than the
   UMAPI client, so this solution may not work for Sign Sync

2. Add the relevant hosts to an allowlist so they aren't subject to filtering or
   inspection. See [above](#hostname-allowances).

3. As a last resort, use the
   [`ssl_verify` configuration option](connect_adobe.md#ssl_verify) to disable
   SSL verification. **Note**: Enable this option at your own risk. It may
   introduce security risks.

# `/tmp` Directory Restrictions

Certain Linux security practices recommend `/tmp` be remounted with restricted
permissions. If your systems follow this practice, you may be unable to run
the User Sync Tool. The UST requires access to the system's temporary directory
to self-extract and execute. To run the tool, try the either of the following:

* Ensure the user running the UST has read, write and exec permissions on `/tmp`
* Set `TMPDIR` to an alternate location (do not `export` this var)

  Example: `TMPDIR=/my/tmp/dir ./user-sync`

---

[Previous Section](additional_tools.md)  \| [Next Section](deployment_best_practices.md)
