---
layout: default
lang: en
title: Deployment Best Practices
nav_link: Deployment Best Practices
nav_level: 2
nav_order: 90
parent: user-manual
page_id: deployment-best-practices
---

[Previous Section](additional_tools.md)

# Deployment Best Practices
{:."no_toc"}

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# Overview

The User Sync tool is designed to run with limited or no human
interaction, once it is properly configured. You can use a
scheduler in your environment to run the tool with whatever
frequency you need.

- The first few executions of the User Sync Tool can take a long
time, depending on how many users need to be added into the Adobe
Admin Console. We recommend that you run these initial executions
manually, before setting it up to run as a scheduled task, in
order to avoid having multiple instances running.
- Subsequent executions are typically faster, as they only need
to update user data as needed. The frequency with which you
choose to execute User Sync depends on how often your
enterprise directory changes, and how quickly you want the changes
to show up on the Adobe side.
- Running User Sync more often than once every 2 hours is not recommended.

# Security Recommendations

Given the nature of the data in the configuration and log files,
a server should be dedicated for this task and locked down with
industry best practices. It is recommended that a server that
sits behind the enterprise firewall be provisioned for this
application. Only privileged users should be able to connect to
this machine. A system service account with restricted privileges
should be created that is specifically intended for running the
application and writing log files to the system.

The application makes GET and POST requests of the User
Management API against a HTTPS endpoint. It constructs JSON data
to represent the changes that need to be written to the Admin
console, and attaches the data in the body of a POST request to
the User Management API.

To protect the availability of the Adobe back-end user identity
systems, the User Management API imposes limits on client access
to the data.  Limits apply to the number of calls that an
individual client can make within a time interval, and global
limits apply to access by all clients within the time period. The
User Sync tool implements back off and retry logic to prevent the
script from continuously hitting the User Management API when it
reaches the rate limit. It is normal to see messages in the
console indicating that the script has paused for a short amount
of time before trying to execute again.

Starting in User Sync 2.1, there are two additional techniques available
for protecting credentials.  The first uses the operating system credential
store to store individual configuration credential values.  The second uses
a mechanism you must provide to securely store the entire configuration file for umapi
and/or ldap which includes all the credentials required.  These are
detailed in the next two sections.

## Storing Credentials in OS Level Storage

To set up User Sync to pull credentials from the OS keyring (e.g. Windows Credential Manager), set the connector-umapi.yml and connector-ldap.yml files as follows:

connector-umapi.yml

	server:
	
	enterprise:
	  org_id: your org id
	  secure_client_id_key: client_id
	  secure_client_secret_key: umapi_client_secret
	  tech_acct_id: your tech account@techacct.adobe.com
	  secure_priv_key_data_key: umapi_private_key_data

Note the change of `client_id`, `client_secret`, and `priv_key_path` to `secure_client_id_key`, `secure_client_secret_key`, and `secure_priv_key_data_key`, respectively.  These alternate configuration values give the key names to be looked up in the user keychain (or the equivalent service on other platforms) to retrieve the actual credential values.  In this example, the credential key names are `umapi_client_id`, `umapi_client_secret`, and `umapi_private_key_data`.

The contents of the private key file is used as the value of `umapi_private_key_data` in the credential store.  This can only be done on platforms other than Windows.  See below for how to secure the
private key file on Windows.

The credential values will be looked up in the secure store using org_id as the username value and the key names in the config file as the key name.

A slight variant on this approach is available (in User Sync version 2.1.1 or later) to encrypt the
private key file using the standard RSA encrypted representation for private keys (known as the
PKCS#8 format).  This approach must be used on Windows because the Windows secure store is not
able to store strings longer than 512 bytes which prevents its use with private keys. This approach
can also be used on the other platforms if you wish.

To store the private key in encrypted format proceed as follows.  First, create an encrypted
version of the private key file.  Select a passphrase and encrypt the
private key file:

    openssl pkcs8 -in private.key -topk8 -v2 des3 -out private-encrypted.key

On Windows, you will need to run openssl from Cygwin or some other provider; it is not included
in the standard Windows distribution.

Next, use the following configuration items in connector-umapi.yml.  The last two items below cause
the decryption passphrase to be obtained from the secure credential store, and reference the encrypted
private key file, respectively:

	server:
	
	enterprise:
	  org_id: your org id
	  secure_client_id_key: umapi_client_id
	  secure_client_secret_key: umapi_client_secret
	  tech_acct_id: your tech account@techacct.adobe.com
	  secure_priv_key_pass_key: umapi_private_key_passphrase
	  priv_key_path: private-encrypted.key

Finally, add the passphrase to the secure store as an entry with the username or url as the org Id, the key
name as `umapi_private_key_passphrase` to match the `secure_priv_key_pass_key` config file entry, and the value
as the passphrase.  (You can also inline the encrypted private key by placing the data in the
connector-umapi.yml file under the key `priv_key_data` instead of using `priv_key_path`.)

This ends the description of the variant where the RSA private key encryption is used.

connector-ldap.yml

	username: "your ldap account username"
	secure_password_key: ldap_password 
	host: "ldap://ldap server name"
	base_dn: "DC=domain name,DC=com"

The LDAP access password will be looked up using the specified key name
(`ldap_password` in this example) with the user being the specified username
config value.

Credentials are stored in the underlying operating system secure store.  The specific storage system depends in the operating system.

| OS | Credential Store |
|------------|--------------|
| Windows | Windows Credential Vault |
| Mac OS X | Keychain |
| Linux | Freedesktop Secret Service or KWallet |
{: .bordertablestyle }

On Linux, the secure storage application would have been installed and configured by the OS vendor.

The credentials are added to the OS secure storage and given the username and credential id that you will use to specify the credential.  For umapi credentials, the username is the organization id.  For the LDAP password credential, the username is the LDAP username.  You can pick any identifier you wish for the specific credentials; they must match between what is in the credential store and the name used in the configuration file.  Suggested values for the key names are shown in the examples above.

# Scheduling Recommendations

The User Sync Tool is designed to run with limited to no human interaction and can leverage a scheduler feature to run the tool.  Our recommendation is to run the tool no more than once every 2 hours.  

To further prevent customers from experiencing degraded performance, Adobe will add sync controls to the scheduling feature in February 2021.  The new controls will prevent the start of a new session if the system is still running a previous sync from a User Sync Tool integration, resulting in a delayed start time of the subsequent sync call.

To learn more, please visit our [User Management API Documentation](https://adobe-apiplatform.github.io/umapi-documentation/en/).

# Scheduled Task Examples

You can use a scheduler provided by your operating system to run
the User Sync tool periodically, as required by your
enterprise. These examples illustrate how you might configure the
Unix and Windows schedulers.

You may want to set up a command file that runs UserSync with
specific parameters and then extracts a log summary and emails it
to those responsible for monitoring the sync process. These
examples work best with console log level set to INFO

```YAML
logging:
  console_log_level: info
```

## Run with log analysis in Windows

The following example shows how to set up a batch file `run_sync.bat` in
Windows.

```sh
C:\\...\\user-sync.exe --users file users-file.csv --process-groups | findstr /I "WARNING ERROR CRITICAL ---- ==== Number" > temp.file.txt
rem email the contents of temp.file.txt to the user sync administration
sendmail -s “Adobe User Sync Report for today” UserSyncAdmins@example.com < temp.file.txt
```

*NOTE*: Although we show use of `sendmail` in this example, there
is no standard email command-line tool in Windows.  Several are
available commercially.

## Run with log analysis on Unix platforms

The following example shows how to set up a shell file
`run_sync.sh` on Linux or Mac OS X:

```sh
user-sync --users file users-file.csv --process-groups | grep "CRITICAL\|WARNING\|ERROR\|=====\|-----\|number of\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” UserSyncAdmins@example.com
```

## Schedule a Sync

### Cron

This entry in the Unix crontab will run the User Sync tool at 4
AM each day:

```text
0 4 * * * /path/to/run_sync.sh
```

Cron can also be setup to email results to a specified user or
mailing list. Check the documentation on cron for your system
for more details.

### Windows Task Scheduler

This command uses the Windows task scheduler to run the User Sync
tool every day starting at 4:00 PM:

```text
schtasks /create /tn "Adobe User Sync" /tr C:\path\to\run_sync.bat /sc DAILY /st 16:00
```

Check the documentation on the windows task scheduler (`help
schtasks`) for more details.

There is also a GUI for managing windows scheduled tasks. You can
find the Task Scheduler in the Windows administrative control
panel.

## Log File Rotation

The default name of the log file produced by each run of User Sync changes on a daily basis,
which provides a sort of "poor man's log file rotation" where all prior days are saved
uncompressed in the same directory.  Should you wish to use a log file rotation utility,
you will probably want to fix the name of the log produced, so that your utility can
monitor the size of the log and do rotation on its own schedule.  In order to do this,
just define the `log_file_name_format` so that it has the desired string value, without
any formatting directives.  For example, if you wanted to have the log named "user-sync.log"
in all cases, you would put this setting in your configuration file.

```yaml
logging:
  log_file_name_format: "user-sync.log"
```

# Disabling SSL Verification

In environments where SSL inspection is enforced at the firewall, the https requests can encounter an error similar to the following:

`CRITICAL main - UMAPI connection to org id 'someUUIDvalue@AdobeOrg' failed: [SSL: CERTIFICATE_VERIFY_FAILED] `

This is because the requests module is not aware of the middle-man certificate required for SSL inspection.  The recommended solution to this problem is to specify a path to the certificate bundle using the  REQUESTS_CA_BUNDLE environment variable (see https://helpx.adobe.com/enterprise/kb/UMAPI-UST.html for details).  However, in some cases following these steps does not solve the problem.  The next logical step is to disable SSL inspection on the firewall.  If, however, this is not permitted, you may work around the issue by disabling SSL verification for user-sync.  

Disabling the verification is unsafe, and leaves requests vulnerable to middle man attacks, so it is recommended to  avoid disabling it if at all possible.  The umapi client only ever targets secure Adobe URL's.  In addition, since this option is only recommended for use in a secure network environment, any potential risk is further mitigated.

To bypass the ssl verification, update the user-sync-config.yml as follows:

```yaml
invocation_defaults:
  ssl_cert_verify: False
```

During the calls, you may also see a warning from requests:

"InsecureRequestWarning: Unverified HTTPS request is being made to host 'usermanagement.adobe.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
  InsecureRequestWarning"

# Restricted /tmp Access

Certain Linux security practices recommend `/tmp` be remounted with restricted permissions. If your systems follow this practice, you may be unable to run the User Sync Tool. The UST requires access to the system's temporary directory to self-extract and execute. To run the tool, try the following:

* Ensure the user running the UST has read, write and exec permissions on `/tmp`
* Set `TMPDIR` to an alternate location (do not `export` this var)

  Example: `TMPDIR=/my/tmp/dir ./user-sync`

---

[Previous Section](additional_tools.md)

