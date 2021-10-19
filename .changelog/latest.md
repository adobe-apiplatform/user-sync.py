# New Features

## Credential Management

* Save plantext secrets automatically to OS keychain
* Convert from plaintext config keys to secure config keys
* Supports UMAPI private key encryption
* More info - https://github.com/adobe-apiplatform/user-sync.py/blob/v2-multi-dir-cred/docs/en/user-manual/additional_tools.md

## Support for Multiple Identity Sources

* UST can now sync from more than one identity source at a time
* All types supported - `ldap`, `csv`, `adobe_console` and `okta`
* Mutiple sources of a given type can be used
* Group mappings can apply to all sources or refer to specific sources
* More info - https://github.com/adobe-apiplatform/user-sync.py/blob/v2-multi-dir-cred/docs/en/user-manual/advanced_configuration.md#working-with-multiple-identity-source
