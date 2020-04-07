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

#### Documentation goes here

###Credential Manager

The user can manage credentials from the command line using the 
```credentials``` command with any of the
following subcommands.

| Subcommand | Description |
|------------------------------|------------------|
| `store` | Stores all sensitive credentials for the User Sync Tool in OS Secure storage, then replaces the plaintext values in the configuration files with secure keys. |
| `retrieve` | Retrieves all stored credentials for the User Sync Tool from OS secure storage and prints them to the console. |
| `revert` | Retrieves all stored credentials for the User Sync Tool from OS Secure storage, then replaces secure keys in the configuration files with the retrieved plaintext values. |
| `get` | Takes one parameter `--identifier [identifier]` either as a command line option or from a user prompt. Keyring then retrieves the corresponding credential from the backend. |
| `set` | Takes two parameters, `--identifier [identifier]` and `--value [value]` either as command line options or from user prompts. Keyring then creates a new credential in the backend for the specified identifier. The username will be "user_sync." |

**Sample Output (Windows)**

Successful output from ```set``` subcommand:

```
(venv) C:\Program Files\Adobe\Adobe User Sync Tool>python user-sync.pex credentials set
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
(venv) C:\Program Files\Adobe\Adobe User Sync Tool>python user-sync.pex credentials set --identifier ldap_password --value password
Using backend: Windows WinVaultKeyring
Setting 'ldap_password' in keyring
Using keyring 'Windows WinVaultKeyring' to set 'ldap_password'
Validating...
Using keyring 'Windows WinVaultKeyring' to retrieve 'ldap_password'
Credentials stored successfully for: ldap_password
```

Successful output from ```get``` subcommand. Note that the 
output echoes the requested identifier and password on the last line:

```
(venv) C:\Program Files\Adobe\Adobe User Sync Tool>python user-sync.pex credentials get
Enter identifier: ldap_password
Using backend: Windows WinVaultKeyring
Getting 'ldap_password' from keyring
Using keyring 'Windows WinVaultKeyring' to retrieve 'ldap_password'
ldap_password: password
```

Similar to ```set```, ```get``` can also be run without the prompt by
passing in the identifier as a parameter.

The ```store``` subcommand does not take any parameters. Rather,
it will automatically place all sensitive credentials contained in
the configuration files specified in ```user-sync-config.yml``` in
OS Secure storage. This snippet 
of ```connector-ldap.yml``` shows the unsecured credential prior to running ```store```:

```
username: ldapuser@example.com
password: ldap_password
host: ldap://host
```

After running ```store```, the value of the sensitive key will be replaced with a 
new key-value pair in which the key is the string "secure" and the value is 
the absolute path to the configuration file appended
with ":" and the original key as shown below.

```
username: ldapuser@example.com
password: 
    secure: C:\Program Files\Adobe\Adobe User Sync Tool\connector-ldap.yml:password
host: ldap://host
```

In the example above, Keyring has used ```C:\Program Files\Adobe\Adobe User Sync Tool\connector-ldap.yml:password```
as the identifier (called "Internet or Network Address" on Windows)
in OS Secure storage.

Successful console output after running the ```store``` command:

```
(venv) C:\Program Files\Adobe\Adobe User Sync Tool>python user-sync.pex credentials store
   <output from store goes here>
```

Similar to ```store```, ```retrieve``` does not take any arguments. Rather, 
it will automatically read the configuration files specified in 
```user-sync-config.yml``` to find the values that have been stored securely.
Then it uses Keyring to retrieve these values from OS Secure storage. These
credentials will be printed to the console, but the configuration files
will remain in their secure state. Successful output is shown below.

```
(venv) C:\Program Files\Adobe\Adobe User Sync Tool>python user-sync.pex credentials retrieve
   <output from retrieve goes here>
```

The ```revert``` subcommand is essentially the inverse of ```store```.
It will replace any secured keys in the configuration 
files with their original plaintext values. Note that OS Secure storage
will still hold these credentials even after running revert.

Successful output from ```revert``` is shown below.

```
(venv) C:\Program Files\Adobe\Adobe User Sync Tool>python user-sync.pex credentials revert
   <output from revert goes here>
```



[Previous Section](deployment_best_practices.md)