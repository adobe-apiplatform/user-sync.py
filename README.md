# aedash-connector
Connector for Enterprise Dashboard User Management

# Overview

The Adobe Enterprise Dashboard Connector automates user creation and product entitlement provisioning in the Enterprise Dashboard.  It takes a list of enterprise directory users, either from an LDAP connection, or from a tab-separated file, and creates, updates, or disables user accounts in the Dashboard.

# Requirements

* Python 2.7+
* User Management API Credentials (see [the official documentation](https://www.adobe.io/products/usermanagement/docs/gettingstarted))
* Accessible LDAP server (optional)

# Installation

The connector is packaged as a [self-contained .pex file](https://github.com/pantsbuild/pex).  See the releases page to get the latest build for your platform.

## Build Instructions

Requirements:

* Python 2.7+
* [virtualenv](https://virtualenv.pypa.io/en/stable/)
* If building on Debian - `python-dev libssl-dev libffi-dev libsasl2-dev libldap2-dev`
* GNU Make

To build, run `make pex` from the command line in the main repo directory.

# Basic Usage

```
usage: aedc [-h] [-i INFILE] [-V] -c CONFIG_PATH -a AUTH_STORE_PATH

Adobe Enterprise Dashboard User Management Connector

optional arguments:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        input file - reads from stdin if this parameter is
                        omitted
  -V, --version         show program's version number and exit

required arguments:
  -c CONFIG_PATH, --config CONFIG_PATH
                        API Config Path
  -a AUTH_STORE_PATH, --auth-store AUTH_STORE_PATH
                        Auth Store Path
```

The connector requires two arguments to be specified.

## `--config`

Path to config file.  See "Configuration" section for more information.

## `--auth`

Path to auth token store file.  The connector will create the store file if it doesn't already exist, and initialize it with a new authentication token.

# Configuration

See `example-config.yml` for a configuration template.

The config file is divided into two sections - integration and domains.  These are represented as keys in config YAML.

## `integration`

The integration section configures the keys, IDs, and endpoints for interacting with the API.  Most of the details in this section come from the integration page on [adobe.io](http://adobe.io).

This section contains two subsections - `server` and `enterprise`.

`server` specifies the hostnames and endpoints for the API itself, as well as IMS authentication.

Example:

```
  server:
    host: usermanagement.adobe.io
    endpoint: /v2/usermanagement
    ims_host: ims-na1.adobelogin.com
    ims_endpoint_jwt: /ims/exchange/jwt
```

`enterprise` contains the Organization ID, API Key, API Secret, etc.

Example:

```
  enterprise:
    org_id: [ORG ID]
    api_key: [API KEY]
    client_secret: [CLIENT SECRET]
    tech_acct: [TECH ACCT ID]
    priv_key_path: /path/to/private.key
```

## `domains`

`domains` contains domain-specific configuration.  Each domain config object is keyed by the domain name.

Each domain key contains the configuration for that domain - the domain type (federated or enterprise), LDAP connection & query details, and security group/product group mappings.

# Supported Workflows
