---
layout: default
lang: en
title: Syncing From a CSV File
nav_link: Sync From CSV
nav_level: 2
nav_order: 45
parent: user-manual
page_id: sync-from-csv
---

[Previous Section](sync_from_console.md)  \| [Next Section](usage_scenarios.md)

# Syncing From a CSV File
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

To offer some level of compatibility with unsupported identity sources, the User Sync Tool
can synchronize users from a CSV file. CSV (comma or character separated values) is a simple
format that structures data according to a few rules.

1. One record per line
2. Data fields are separated by a special character (typically comma (`,`), pipe (`|`) or tab). The
   `csv` connector uses comma (`,`) by default. The separator is configurable.
3. Optional header row
4. Most CSV dialects specify an escape mechanism for dealing with fields that contain a literal
   separator character. The CSV reader used by the User Sync Tool uses double quote `"` characters to
   encapsulate fields that contain literal separators.

When working with a CSV identity source file, keep in mind that the Sync Tool treats the CSV
as it does any other identity source - it expects a full snapshot of user state which it
will use to maintain user state in the Admin Console.

# Usage

The Sync Tool's `csv` connector does not require a configuration file. We recommend
getting a [template CSV](https://github.com/adobe-apiplatform/user-sync.py/blob/v2/examples/csv%20inputs%20-%20user%20and%20remove%20lists/users-file.csv)
from the source repository. There is also a template CSV file packaged with the
examples bundle available with [every release](https://github.com/adobe-apiplatform/user-sync.py/releases/latest).

The User Sync Tool can be invoked in two different ways when using a CSV identity file.
We recommend using the `csv` connector option instead of `users`.

| Invocation Default | CLI Option |
|---|---|
| `users: ['file', 'users.csv']` | `--users file users.csv` |
| `connector: ['csv', 'users.csv']` | `--connector csv users.csv` |

Either option will invoke the same `csv` connector component. If the `users` option is in use,
then the `connector` setting is overidden.

# CSV Format

The column names of the CSV input file are customizable (see below). This example shows the header
row expected by default.

```
firstname,lastname,email,country,groups,type,username,domain
John,Smith,jsmith@example.com,US,"AdobeCC-All",enterpriseID,,
Jane,Doe,jdoe@example.com,US,"AdobeCC-All",federatedID,,
Richard,Roe,rroe@example.com,US,"AdobeCC-All",,,
```

## `firstname`

(optional)

The first name (given name) of a user.

## `lastname`

(optional)

The last name (surname) of a user.

## `email`

(**required**)

User's email address. Domain must be claimed to directory owned or trusted by target console.

## `country`

(**required**)

User's country code. Must be a valid [ISO-3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code.

If left blank, will be overridden by `default_counry_code` in `user-sync-config.yml`.

## `groups`

(optional)

Comma-delimited list of "directory" groups. These are basically virtual groups. They can correspond to groups
assigned in an upstream identity system, but they don't have to. The import thing is that they correspond
to `directory_group`s in the group mapping.

Each group name must be separated by a comma `,` with no trailing space.

Simple example:

```
group1,group2,group3
```

If `delimiter` in `connector-csv.yml` is set to `','` (the default) then `group` assignments with more
than one group should use double quotes to escape the literal commas present in the field.

```
Test,User,test.user@example.com,US,"group1,group2,group3",federatedID,,
```

## `type`

(optional)

Defines the identity type of a user. Valid options are `adobeID`, `enterpriseID` and `federatedID`. If this
field is blank, the `identity_type` as specified in `user-sync-config.yml` will be used.

## `username`

(optional)

Defines the username. The normal username rules apply:

* Can be alphanumeric (not in email form) as long as `domain` is populated
* Can be email-like as long as `domain` is empty
* If username is email-type then domain must be claimed to same directory as `email` domain
* Username cannot be set for `adobeID` or `enterpriseID` users

## `domain`

(optional)

Defines domain name for non-email `username`s. Must be claimed to same directory as `email` domain.

# Configuration

The optional config file can be used to customize the expected format of the CSV input file.

The CSV connector is named `connector-csv.yml` by default. A template configuration file can be
found [here](https://github.com/adobe-apiplatform/user-sync.py/blob/v2/examples/config%20files%20-%20basic/connector-csv.yml)
or in the examples bundle available with [every release](https://github.com/adobe-apiplatform/user-sync.py/releases/latest).

The CSV connector config can be enabled in `user-sync-config.yml` under `directory_users`.

```yaml
directory_users:
  connectors:
    csv: connector-csv.yml
```

This will enable configuration for the `csv` connector. Note that the configuration file will be
read and applied regardless of which invocation method (`connector` or `users`) is used to
use the CSV file as the identity source.

## Format Options

### `delimiter`

(optional)

Defines the character that separates fields in the CSV file. Set to comma (`,`) by default.

**Note:** Regardless of the separator, literal separator characters present in data fields
are always escaped by enclosing the field with double quotes (`"`).

### `string_encoding`

(optional)

Defines the character encoding of the input CSV file. Default is `utf-8`.

Any encoding type listed [here](https://docs.python.org/3.9/library/codecs.html#standard-encodings)
is potentially valid.

It is generally better to keep the encoding set to `utf-8` and reformat the CSV file to UTF-8.
As per the linked documentation, certain encoding type aliases can process more slowly. And
sometimes malformed input files can be mistaken for other encodings which can lead to problems.

## Column Mapping Options

The header row column names of the CSV file can be fully customized. The following options
can be used to redefine any column name.

| Config Option | Redefines Column Name |
|---|---|
| `email_column_name` | `email` |
| `first_name_column_name` | `firstname` |
| `last_name_column_name` | `lastname` |
| `country_column_name` | `country` |
| `groups_column_name` | `groups` |
| `identity_type_column_name` | `identity_type` |
| `username_column_name` | `username` |
| `domain_column_name` | `domain` |

---

[Previous Section](sync_from_console.md)  \| [Next Section](usage_scenarios.md)
