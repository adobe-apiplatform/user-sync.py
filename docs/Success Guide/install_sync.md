## Install user sync

Once you have access to the server where user sync will run, pick a directory where you will install and operate user sync.

On Windows, you will need to install Python.  As of this writing, version 2.7.13 is recommended.  Windows and Python need to be 64 bit versions.

On Windows, you also are very likely to need to set an environment variable PEX_ROOT to C:\user_sync\.pex.  This is needed to work around Windows pathname length limits.

The next few slides show the installation process.

To find the latest release:  Start here: 
https://github.com/adobe-apiplatform/user-sync.py

![install](images/install_finding_releases.png)

Select “release”


Download the the examples.config.tar.gz, User Sync Guide, and build for your platform, osx, ubuntu, windows, or centos.

![install2](images/install_release_screen.png)

Setup a folder to contain the user sync tool and config files.

Place the user-sync file for your OS in the folder.

Windows only: You’ll need to install Python (2.7.13 or later, 64 bit) on the machine also.

Copy in the example config files, also.

![install2](images/install_config_files.png)
