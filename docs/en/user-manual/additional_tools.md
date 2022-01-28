---
layout: default
lang: en
nav_link: Additional Tools
nav_level: 2
nav_order: 80
---


# Additional Tools

---

[Previous Section](deployment_best_practices.md)

---

## Credential Manager

The user can manage credentials from the command line using the 
`credentials` command with any of the
following subcommands.

| Subcommand | Description |
|------------------------------|------------------|
| `store` | Stores all sensitive credentials for the User Sync Tool in OS Secure storage, then replaces the plaintext values in the configuration files with secure keys. |
| `retrieve` | Retrieves all stored credentials for the User Sync Tool from OS secure storage and prints them to the console. |
| `revert` | Retrieves all stored credentials for the User Sync Tool from OS Secure storage, then replaces secure keys in the configuration files with the retrieved plaintext values. |
| `get` | Takes one parameter `--identifier [identifier]` either as a command line option or from a user prompt. Keyring then retrieves the corresponding credential from the backend. |
| `set` | Takes two parameters, `--identifier [identifier]` and `--value [value]` either as command line options or from user prompts. Keyring then creates a new credential in the backend for the specified identifier. The username will be "user_sync." |

**Sample Output (Windows)**

Successful output from `set` subcommand:

```
C:\Program Files\Adobe\Adobe User Sync Tool>user-sync.exe credentials set
Enter identifier: ldap_password
Enter value:
Using backend: Windows WinVaultKeyring
Setting 'ldap_password' in keyring
Using keyring 'Windows WinVaultKeyring' to set 'ldap_password'
Validating...
Using keyring 'Windows WinVaultKeyring' to retrieve 'ldap_password'
Credentials stored successfully for: ldap_password
```
The identifier and value (password) can also be set as parameters:

```
C:\Program Files\Adobe\Adobe User Sync Tool>user-sync.exe credentials set --identifier ldap_password --value password
Using backend: Windows WinVaultKeyring
Setting 'ldap_password' in keyring
Using keyring 'Windows WinVaultKeyring' to set 'ldap_password'
Validating...
Using keyring 'Windows WinVaultKeyring' to retrieve 'ldap_password'
Credentials stored successfully for: ldap_password
```

Successful output from `get` subcommand. Note that the 
output echoes the requested identifier and password on the last line:

```
C:\Program Files\Adobe\Adobe User Sync Tool>user-sync.exe credentials get
Enter identifier: ldap_password
Using backend: Windows WinVaultKeyring
Getting 'ldap_password' from keyring
Using keyring 'Windows WinVaultKeyring' to retrieve 'ldap_password'
ldap_password: password
```

Similar to `set`, `get` can also be run without the prompt by
passing in the identifier as a parameter.

The `store` subcommand does not take any parameters. Rather,
it will automatically place all sensitive credentials contained in
the configuration files specified in `user-sync-config.yml` in
OS Secure storage. This snippet 
of `connector-ldap.yml` shows the unsecured credential prior to running `store`:

```
username: ldapuser@example.com
password: ldap_password
host: ldap://host
```

After running `store`, the value of the sensitive key will be replaced with a 
new key-value pair in which the key is the string "secure" and the value is 
the absolute path to the configuration file appended
with ":" and the original key as shown below.

```
username: ldapuser@example.com
password: 
    secure: C:\Program Files\Adobe\Adobe User Sync Tool\connector-ldap.yml:password
host: ldap://host
```

In the example above, Keyring has used `C:\Program Files\Adobe\Adobe User Sync Tool\connector-ldap.yml:password`
as the identifier (called "Internet or Network Address" on Windows)
in OS secure storage.

The `connector-umapi.yml` configuration file contains two sensitive keys (`client_id` and `client_secret`) as well as either `priv_key_path` (with the path to the `private.key` file) or `priv_key_data` with the value stored in-line. If the file uses `priv_key_path` and the key has not been encrypted, the console will prompt the user asking if they want to encrypt the private key. If yes, it will prompt the user to create a password and then confirm it. This action adds a new key to `connector-umapi.yml` called `priv_key_pass`, which will automatically be stored in OS secure storage along with the other sensitive keys. If no, the key remains unencrypted in the file.

If the user has put the key data in-line under `priv_key_data`, the Sync Tool will attempt to store the key data in OS secure storage. If successful, the key data will stored just like the other sensitive values. If unsuccessful (this can happen due to character limits in the default Windows credential store), the Sync Tool will take the user through the encryption prompts described above. The result is that the key data has been replaced with encrypted key data, and the key `priv_key_pass` has been added to `connector-umapi.yml` and its value subsequently stored.

Below is the successful console output after running the `store` command where the `connector-umapi.yml` file uses `priv_key_path`:

```
C:\Program Files\Adobe\Adobe User Sync Tool>user-sync.exe credentials store
Using keyring: cryptfile CryptFileKeyring
Create password : [console input will be hidden]
Repeat for confirmation:
Encrypted private key file saved to: 'private.key'
'['enterprise', 'priv_key_pass']' added to 'C:\Program Files\Adobe\UST_MultiCred_RC1\connector-umapi.yml' and stored securely.
The following keys were stored:

connector-ldap.yml:
  password

connector-umapi.yml:
  enterprise:client_id
  enterprise:client_secret
```

Similar to `store`, `retrieve` does not take any arguments. Rather, 
it will automatically read the configuration files specified in 
`user-sync-config.yml` to find the values that have been stored securely.
Then it uses Keyring to retrieve these values from OS secure storage. These
credentials will be printed to the console, but the configuration files
will remain in their secure state. Successful output is shown below.

```
C:\Program Files\Adobe\Adobe User Sync Tool>user-sync.exe credentials retrieve
Using keyring: cryptfile CryptFileKeyring

connector-ldap.yml:
  password: [ldap password displayed in plaintext]

connector-umapi.yml:
  enterprise:client_id: [client_id displayed in plaintext]
  enterprise:client_secret: [client_secret displayed in plaintext]
  enterprise:priv_key_pass: [private key password displayed in plaintext]
```

The `revert` subcommand is essentially the inverse of `store`.
It will replace any secured keys in the configuration 
files with their original plaintext values. Note that OS Secure storage
will still hold these credentials even after running revert.

Successful output from `revert` is shown below.

```
C:\Program Files\Adobe\Adobe User Sync Tool>user-sync.exe credentials revert
Using keyring: cryptfile CryptFileKeyring
The following keys were reverted to plaintext:

connector-ldap.yml:
  password

connector-umapi.yml:
  enterprise:client_id
  enterprise:client_secret
  enterprise:priv_key_pass
```

<br/>

---
## Certificate Generation

```
user-sync certgen [optional parameters]
```

User Sync Tool includes built in X509 certificate/key pair generator which is suitable for creating the UMAPI integration. The cert generator can be invoked from the command line using "user-sync certgen" [OPTIONS] to generate a new certificate/key pair with random or user-specified subjects. User Sync Tool can use these files to communicate with the admin console. Please visit [Adobe.IO](https://console.adobe.io) to complete the integration process.


| Parameters&nbsp;and&nbsp;argument&nbsp;specifications | Description |
|------------------------------|------------------|
| `-r`<br />`--randomize` | Specifying `-r` or `--randomize` will randomize the subjects for the certificate. No user input is required when using this option. |
| `-y`<br />`--overwrite` | Specifying `-y` or `--overwrite` will overwrite files without having to confirm.   |
| `-p` _filename_<br />`--private-key-file`  _filename_ | Specifying `-p` or` --private-key-file` will set a custom output path for the private key. Absolute or relative to the working folder. The default is private.key. |
| `-c` _filename_<br />`--cert-pub-file` _filename_ | Specifying `-c` or `--cert-pub-file` will set a custom output path for the public certificate. Absolute or relative to the working folder. The default is certificate_pub.crt. |
{: .bordertablestyle }
<br/>
<h3>Example #1</h3>

```
> python user-sync.pex certgen

Enter information as required to generate the X509 certificate/key pair for your organization. This information is used only for authentication with UMAPI and does not need to reflect
an SSL or other official identity.
Expiration date (mm/dd/yyyy) [02/04/2030]: 02/04/2030
Country Code [US]: US
State [Your State]: MN
City [Your City]: Minneapolis
Organization [Company]: Company, Inc.
Common Name [Your Name]: John Doe
Email [email<span>@</span>company.com]: email<span>@</span>company.com
Files were created at:
//path/to/private.key
//path/to/certificate_pub.crt
```


In the example above, we entered some information about our organization, location, etc. As indicated by the program output, these fields will not be used by Adobe to identify you or your organization; and therefore, you may fill in these fields as you deem correct.
You can also use` --randomize` to produce a secure random subject and automate the Certgen process (no user input will be required).


<h3>Example #2</h3>

```
> python user-sync.pex certgen –randomize
```

In this case, a certificate was created with the following random attributes. This certificate will not expire for 10 years.
```
Email = fcc626a96eec
Common Name = 5b61dd368ea8
Organization = 39d2b95b0c4a
Locale = d10111c9101f
State = cec8268e8b05
Country = 6d
```

You can use certificate_pub to create your UMAPI integration and private key to [configure connector-umapi.yml](configuring_user_sync_tool.html#connector-umapiyml). <br/><br/>

---

## Private Key Encryption

```
user-sync encrypt [optional parameters]
user-sync decrypt [optional parameters]
```

Private key encryption allows a user to encrypt a private key file with a passphrase. The UST can be configured to read this passphrase from a stored value from the priv_key_pass in the connector-umapi.yml file. When the UST runs, a decrypted version of the private key file is read without being stored. The decrypt command will allow a user to decrypt the private key file when the correct passphrase is entered. The decrypted data will overwrite the data in the private key file.


| Parameters&nbsp;and&nbsp;argument&nbsp;specifications | Description |
|------------------------------|------------------|
| `key-path` _filename_ | Provide an absolute or relative filename for the private key to be encyrpted/decrypted. The default is private.key |
| `-p`<br />`--password` | Password will be prompted if not passed as a parameter. This will be used as the passphrase for the RSA encryption of the private key file.  |
{: .bordertablestyle }


[Previous Section](deployment_best_practices.md)