# user-sync.py: User Sync Tool from Adobe

The User Sync Tool is a command-line tool that automates the creation and management of Adobe user accounts.  It
does this by reading user and group information from an organization's enterprise directory system or a file and 
then creating, updating, or removing user accounts in the Adobe Admin Console. The key goals of the User Sync 
Tool are to streamline the process of named user deployment and automate user management for all Adobe users and products.

This application is open source, maintained by Adobe, and distributed under the terms
of the OSI-approved MIT license.  See the LICENSE file for details.

Copyright (c) 2016-2017 Adobe Inc.

## Documentation

The [User Sync Documentation](https://adobe-apiplatform.github.io/user-sync.py/) covers all aspects of the tool, from both a general and a technical point of view.  The following links are good places to start:

- [Non-Technical Primer](https://spark.adobe.com/page/E3hSsLq3G1iVz/)
- [User Manual](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/)
- [Step-by-Step Setup](https://adobe-apiplatform.github.io/user-sync.py/en/success-guide/)

## System Requirements

To run User Sync, you must have an up-to-date 64-bit Python installed on your system, either Python 2.7 or Python 3.4+.  In addition you must have User Management API Credentials for your organization (see [the official documentation](https://www.adobe.io/products/usermanagement/docs/gettingstarted))

## Installation and Use

The connector is packaged as a self-contained executable.  See the [releases page](https://github.com/adobe-apiplatform/user-sync.py/releases)
to get the latest build for your platform. Releases are distributed as archives (`.zip` or `.tar.gz`). Each release file
contains the UST executable.

* On Linux systems, the executable is named `user-sync`.
* On Windows systems, the executable is named `user-sync.exe`.

After downloading and extracting the tool, verify the tool will work on your system:

* `$ ./user-sync --version` (or `> ./user-sync.exe --version`) 
* `$ ./user-sync --help` (or `> ./user-sync.exe --help`) 

There are a wide variety of command-line arguments; see
[the docs](https://adobe-apiplatform.github.io/user-sync.py/en/user-manual/command_parameters.html) for details.

## Configuration

You will need a personalized User Sync configuration to use the tool effectively.  The documentation includes a [Setup and Success Guide](https://adobe-apiplatform.github.io/user-sync.py/success-guide/) that will take you step-by-step through the configuration process.  In addition, the `examples` directory (also available as a tarball on the [releases page](https://github.com/adobe-apiplatform/user-sync.py/releases)) contains sample configuration files which include all of the possible options with their descriptions and default values.

## Build Instructions

The general procedure to build the User Sync Tool is the same across platforms. However, each platform has its own set of
prerequisites that must be met before following these instructions. Refer to the notes for your platform and return here
to learn how to build the Sync Tool from source.

**NOTE:** Python 3.6 is required on all platforms.

1. Clone this repository `git clone https://github.com/adobe-apiplatform/user-sync.py.git`
2. Create a new Python 3.6 virtual environment `python -m venv /path/to/venv` (note: your system may prompt you to install
   additional packages before creating the virtual environment)
3. Activate the environment `source /path/to/venv/bin/activate` (or `.\path\to\venv\Scripts\activate` on Windows)
4. `cd` to the `user-sync.py` directory
5. Install the Okta client wheel `pip install external/okta-0.0.3.1-py2.py3-none-any.whl`
6. Install the sync tool locally
  1. `pip install -e .`
  2. `pip install -e .[test]`
  3. `pip install -e .[setup]`
7. Create the build by running `make`

If the Sync Tool was built successfully, then the executable can be found in the `dist/` directory. The binary will be named
`user-sync` or `user-sync.exe` depending on platform.

### Ubuntu and other Debian variants

**NOTE:** These prerequisites are known to work on Ubuntu 16.04 or newer, but should work on Debian and other Debian variants.

On Linux, many of the Sync Tool's dependencies are built from source and contain components written in C and other compiled
languages. For this reason, it is necessary to install some system packages and libraries.

```bash
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo apt-get install -y build-essential
sudo apt-get install -y python-dev python-pip python-virtualenv
sudo apt-get install -y pkg-config libssl-dev libdbus-1-dev libdbus-glib-1-dev python-dbus libffi-dev
sudo apt-get install -y python3-dev python3-venv
```

### CentOS and other RedHat variants

**NOTE:** These prerequisites are known to work on CentOS 7 or newer, but should work on Redhat Enterprise Linux and other
Redhat variants.

On Linux, many of the Sync Tool's dependencies are built from source and contain components written in C and other compiled
languages. For this reason, it is necessary to install some system packages and libraries.

```bash
yum groupinstall -y "Development Tools"
yum install -y epel-release
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum install -y python36u-devel python36u-pip python36u-virtualenv
yum install -y python-devel python-pip python-virtualenv
yum install -y pkgconfig openssl-devel dbus-glib-devel dbus-python libffi-devel
```

### macOS

On macOS there are a wide variety of ways to get current Python installations that don't interfere with the system-required Python, and a wide way of creating virtual environments for that Python. We strongly recommend using `pyenv` for installation and maintenance and `pyenv-virtualenv` for virtual environment support.  And we recommend getting those via `homebrew`.  The sequence for this is:

1. Install the latest version of the Apple Developer Command Line Tools via `xcode-select --install`.
1. Install Homebrew per the directions [here](http://docs.brew.sh).
1. Install `openssl` via Homebrew: `brew install openssl`
1. Install `pyenv` via Homebrew: `brew install pyenv`
1. Install `pyenv-virtualenv` via Homebrew: `brew install pyenv-virtualenv`
1. Find your desired Python version with: `pyenv install --list`
1. Install that python with `pyenv install ##`, where `##` is the desired version number.
1. Create a virtual environment for your builds, with `pyenv virtualenv ## myname`.
1. In your `user-sync.py` source directory, activate that virtual environment with `pyenv local myname`.

This sequence not only ensures that you are set up to do Python extension compiles, but also that they will know how to find the openssl libraries, and that you can easily install any other needed development libraries with Homebrew.

In general, regardless of how you get your Python, you will need:

* The latest security updates.
* The latest `openssl` (see above).
* The latest version of XCode and/or the Developer Command Line Tools (see above).
* Installs of modern openssl, ffi, and pkg-config libraries.  With Homebrew, you can do:
    ```bash
    homebrew install pkg-config openssl libffi
    ```
* To know how to include the XCode `include` directory in a compile spawned from `pip` install.  If you didn't do a command line developer tools install (which puts the headers into /usr/include), you can do:
    * `CFLAGS="-I$(xcrun --show-sdk-path) pip install ...`.
* To know how to include a modern `openssl` header path in a `pip` install.  If you installed your Python via Homebrew or `pyenv`, this is taken care of for you, see above.  Otherwise, if you installed ssl with Homebrew, you can do:`CFLAGS="-I$(brew --prefix openssl)/include"  LDFLAGS="-L$(brew --prefix openssl)/lib" pip install ...`.

### Windows

**NOTE:** We recommend installing a Git client build that can be run from Windows Powershell or `cmd.exe`. [Scoop](https://scoop.sh)
provides a package to easily install Git natively. Build instructions are not guaranteed to work in Git Bash.

* Python 3.6 (see python.org for latest 3.6 release)
* [Chocolatey](https://chocolatey.org/)
* [Scoop](https://scoop.sh) (if you need to install Git)
* GNU Make (install with Chocolatey - `choco install make`)
* Git (if not installed) - `scoop install git`

If you already have some other version of Python installed, you will want to use the `py` tool to create the virtual environment.

```
> py -3.6 -m venv \path\to\venv
```

This ensures that the virtual environment is linked to the correct version of Python.

Once all Windows prerequisites are met, refer to the generic build instructions above to complete the build.
