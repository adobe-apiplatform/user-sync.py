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

## Configuration Examples

# Supported Workflows
