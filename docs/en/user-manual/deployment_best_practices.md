---
layout: default
lang: en
nav_link: Deployment Best Practices
nav_level: 2
nav_order: 70
---


# Deployment Best Practices

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[Previous Section](advanced_configuration.md)  \| [Next Section](additional_tools.md)

---

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

## Security recommendations

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

### Storing Credentials in OS Level Storage

To setup User Sync to pull credentials from the Python Keyring OS credential store, set the connector-umapi.yml and connector-ldap.yml files as follows:

connector-umapi.yml

	server:
	
	enterprise:
	  org_id: your org id
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
	  secure_priv_key_data_key: umapi_private_key_data

Note the change of `api_key`, `client_secret`, and `priv_key_path` to `secure_api_key_key`, `secure_client_secret_key`, and `secure_priv_key_data_key`, respectively.  These alternate configuration values give the key names to be looked up in the user keychain (or the equivalent service on other platforms) to retrieve the actual credential values.  In this example, the credential key names are `umapi_api_key`, `umapi_client_secret`, and `umapi_private_key_data`.

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
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
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

### Storing Credentials Via Command Line Argument

The ```credentials``` command allows the user to securely get and
set credentials using either the yaml files or Keyring. This automates
 the process of securing credentials for the user.
 
 ```credentials``` can be run with any of the
following subcommands shown below.

| Subcommand | Description |
|------------------------------|------------------|
| `store` | Replaces the plaintext values of sensitive credentials in yaml files with secure keys. |
| `retrieve` | Retrieves currently stored credentials under the username "user_sync." |
| `revert` | Reverts the yaml files to a plaintext state. |
| `get` | Takes one parameter `--identifier [identifier]` either as a command line option or from a user prompt. Keyring then retrieves the corresponding credential from the backend. |
| `set` | Takes two parameters, `--identifier [identifier]` and `--value [value]` either as command line options or from user prompts. Keyring then creates a new credential in the backend for the specified identifier. The username will be "user_sync." |


### Storing Credential Files in External Management Systems

As an alternative to storing credentials in the local credential store, it is possible to integrate User Sync with some other system or encryption mechanism.  To support such integrations, it is possible to store the entire configuration files for umapi and ldap externally in some other system or format.

This is done by specifying, in the main User Sync configuration file, a command to be executed whose output is used as the umapi or ldap configuration file contents.  You will need to provide the command that fetches the configuration information and sends it to standard output in yaml format, matching what the configuration file would have contained.

To set this up, use the following items in the main configuration file.


user-sync-config.yml (showing partial file only)

	adobe_users:
	   connectors:
	      # umapi: connector-umapi.yml   # instead of this file reference, use:
	      umapi: $(read_umapi_config_from_s3)
	
	directory_users:
	   connectors:
	      # ldap: connector-ldap.yml # instead of this file reference, use:
	      ldap: $(read_ldap_config_from_server)
 
The general format for external command references is

	$(command args)

The above examples assume there is a command with the name `read_umapi_config_from_s3`
and `read_ldap_config_from_server` that you have supplied.

A command shell is launched by User Sync which
runs the command.  The standard output from the command is captured and that
output is used as the umapi or ldap configuration file.

The command is run with the working directory as the directory containing the configuration file.

If the command terminates abnormally, User Sync will terminate with an error.

The command can reference a new or existing program or a script.

Note: If you use this technique for the connector-umapi.yml file, you will want to embed the private key data in connector-umapi-yml directly by using the priv_key_data key and the private key value.  If you use the priv_key_path and the filename containing the private key, you would also need to store the private key somewhere 
secure and have a command that retrieves it in the file reference.

## Scheduled task examples

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

### Run with log analysis in Windows

The following example shows how to set up a batch file `run_sync.bat` in
Windows.

```sh
python C:\\...\\user-sync.pex --users file users-file.csv --process-groups | findstr /I "WARNING ERROR CRITICAL ---- ==== Number" > temp.file.txt
rem email the contents of temp.file.txt to the user sync administration
sendmail -s “Adobe User Sync Report for today” UserSyncAdmins@example.com < temp.file.txt
```

*NOTE*: Although we show use of `sendmail` in this example, there
is no standard email command-line tool in Windows.  Several are
available commercially.

### Run with log analysis on Unix platforms

The following example shows how to set up a shell file
`run_sync.sh` on Linux or Mac OS X:

```sh
user-sync --users file users-file.csv --process-groups | grep "CRITICAL\|WARNING\|ERROR\|=====\|-----\|number of\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” UserSyncAdmins@example.com
```

### Schedule a UserSync task

#### Cron

This entry in the Unix crontab will run the User Sync tool at 4
AM each day:

```text
0 4 * * * /path/to/run_sync.sh
```

Cron can also be setup to email results to a specified user or
mailing list. Check the documentation on cron for your system
for more details.

#### Windows Task Scheduler

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

### Log File Rotation

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

---

[Previous Section](advanced_configuration.md)  \| [Next Section](additional_tools.md)
