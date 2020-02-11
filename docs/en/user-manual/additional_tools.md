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
## Certgen

`user-sync certgen` \[ _optional parameters_ \]

User Sync Tool includes built in X509 certificate/key pair generator which is suitable for creating the UMAPI integration. The cert generator can be invoked from the command line using "user-sync certgen" [OPTIONS] to generate a new certificate/key pair with random or user-specified subjects. User Sync Tool can use these files to communicate with the admin console. Please visit https://console.adobe.io to complete the integration process.


| Parameters&nbsp;and&nbsp;argument&nbsp;specifications | Description |
|------------------------------|------------------|
| `-r`<br />`--randomize` | Specifying `-r` or `--randomize` will randomize the subjects for the certificate. No user input is required when using this option. |
| `-y`<br />`--overwrite` | Specifying `-y` or `--overwrite` will overwrite files without having to confirm.   |
| `-p` _filename_<br />`--private-key-file`  _filename_ | Specifying `-p` or` --private-key-file` will set a custom output path for the private key. Absolute or relative to the working folder. The default is private.key. |
| `-c` _filename_<br />`--cert-pub-file` _filename_ | Specifying `-c` or `--cert-pub-file` will set a custom output path for the public certificate. Absolute or relative to the working folder. The default is certificate_pub.crt. |

#### Example #1

**>python user-sync.pex certgen**

>Enter information as required to generate the X509 certificate/key pair for your organization. This information is used only for authentication with UMAPI and does not need to reflect
>an SSL or other official identity.<br /><br />
>Expiration date (mm/dd/yyyy) [02/04/2030]: **02/04/2030**<br />
>Country Code [US]: **US**<br />
>State [Your State]: **MN**<br />
>City [Your City]: **Minneapolis**<br />
>Organization [Company]: **Company, Inc.**<br />
>Common Name [Your Name]: **John Doe**<br />
>Email [email<span>@</span>company.com]: **email<span>@</span>company.com**<br /><br />
>Files were created at:<br />
>>//path/to/private.key<br />
>>//path/to/certificate_pub.crt<br />

In the example above, we entered some information about our organization, location, etc. As indicated by the program output, these fields will not be used by Adobe to identify you or your organization; and therefore, you may fill in these fields as you deem correct.
You can also use` --randomize` to produce a secure random subject and automate the Certgen process (no user input will be required).


#### Example #2

**> python user-sync.pex certgen –randomize**

In this case, a certificate was created with the following random attributes. This certificate will not expire for 10 years.
>Email = **fcc626a96eec**<br />
>Common Name = **5b61dd368ea8**<br />
>Organization = **39d2b95b0c4a**<br />
>Locale = **d10111c9101f**<br />
>State = **cec8268e8b05**<br />
>Country = **6d**<br />

You can use certificate_pub to create your UMAPI integration and private key to [configure connector-umapi.yml](configuring_user_sync_tool.html#connector-umapiyml).

---

## Private Key Encryption

`user-sync encrypt` \[ _optional parameters_ \]<br />
`user-sync decrypt `\[ _optional parameters_ \]

Private key encryption allows a user to encrypt a private key file with a passphrase. The UST can be configured to read this passphrase from a stored value from the priv_key_pass in the connector-umapi.yml file. When the UST runs, a decrypted version of the private key file is read without being stored. The decrypt command will allow a user to decrypt the private key file when the correct passphrase is entered. The decrypted data will overwrite the data in the private key file.


| Parameters&nbsp;and&nbsp;argument&nbsp;specifications | Description |
|------------------------------|------------------|
| `key-path` _filename_ | Provide an absolute or relative filename for the private key to be encyrpted/decrypted. The default is private.key |
| `-p`<br />`--password` | Password will be prompted if not passed as a parameter. This will be used as the passphrase for the RSA encryption of the private key file.  |



[Previous Section](deployment_best_practices.md)