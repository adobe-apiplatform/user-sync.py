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

```credentials``` can be run with any of the
following subcommands shown below.

| Subcommand | Description |
|------------------------------|------------------|
| `store` | Replaces the plaintext values of sensitive credentials in yaml files with secure keys. |
| `retrieve` | Retrieves currently stored credentials under the username "user_sync." |
| `revert` | Reverts the yaml files to a plaintext state. |
| `get` | Takes one parameter `--identifier [identifier]` either as a command line option or from a user prompt. Keyring then retrieves the corresponding credential from the backend. |
| `set` | Takes two parameters, `--identifier [identifier]` and `--value [value]` either as command line options or from user prompts. Keyring then creates a new credential in the backend for the specified identifier. The username will be "user_sync." |



[Previous Section](deployment_best_practices.md)