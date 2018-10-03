---
layout: default
lang: en
nav_link: Install User Sync
nav_level: 2
nav_order: 270
---

# Install User Sync

[Previous Section](identify_server.md) \| [Back to Contents](index.md) \| [Next Section](setup_config_files.md)

Once you have access to the server where User Sync will run.

There are two methods of installing User Sync Tool.

## Method A (Install Script):

This script will automatically install the required Python, download User Sync Tool, example configuration files and utilities to help with the configuration. This method work for both Windows and Linux.

Run the following command with elevated privileges:

**Windows:**
```powershell
(New-Object System.Net.WebClient).DownloadFile("https://git.io/fY19R","${PWD}\inst.ps1"); .\inst.ps1; rm -Force .\inst.ps1;
```

**Linux/MacOS:**
```shell
sudo sh -c 'wget -O ins.sh https://git.io/fY1SD; chmod 777 ins.sh; ./ins.sh; rm ins.sh;'
```

Note: Server will need to have internet access for this script to work.

[For more information on install script](https://github.com/adobe/UST-Install-Scripts)

## Method B (Manual Installation):

On Windows, you will need to install Python.  As of this writing, version 3.6.x is recommended.  Windows and Python need to be 64 bit versions.

On Windows, you also are very likely to need to set an environment variable PEX\_ROOT to C:\\pex.  This is needed to work around Windows pathname length limits.

Note: Setting PEX\_ROOT may not be necessary if:

- You are running Windows 10
- You are running Python 3.6 or later, 64 bit version (also called X86-64, for AMD64), and
- You have enabled the long pathname support in Windows 10 as described in the Maximum Path Length Limitation section of this [Microsoft Dev Note](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247%28v=vs.85%29.aspx?#maxpath). You can also enable long pathname support by pressing the button in the Python Windows executable installer (in the final dialog box, when installation finishes) that performs this action.

If these conditions are met, you can run without setting PEX\_ROOT.


Initial steps:

&#9744; Setup a user and file directory for installing and running sync.  For example, we'll create a folder /home/user_sync/user_sync_tool and a user user_sync.  On Windows an example would be C:\Users\user_sync\user_sync_tool.

&#9744; Windows only: set the environment variable **PEX\_ROOT** to **C:\pex**. (But see note above.)

&#9744; Windows only: Install python 3.6.2 (or later in the 3.6 series), 64 bit.

The next few sections show the installation process.

To find the latest release:  Start here:
[https://github.com/adobe-apiplatform/user-sync.py](https://github.com/adobe-apiplatform/user-sync.py "https://github.com/adobe-apiplatform/user-sync.py")

![install](images/install_finding_releases.png)

Select “release”


![install2](images/install_release_screen.png)

&#9744; Download the example-configurations.tar.gz, User Sync Guide, and build for your platform, osx, ubuntu, windows, or centos.

&#9744; Decide whether you will run Python 2.x or 3.x (recommended) and download that version of User Sync.  You need to install the corresponding version of Python on your server.

&#9744; Extract the user-sync (or user-sync.pex) file from the archive and place the file for your OS in the folder.  In our example, this would be /home/user_sync/user_sync_tool/user-sync or C:\Users\user_sync\user_sync_tool\user-sync.pex.

&#9744; In the example-configurations.tar.gz file there is a directory **config files - basic**.  From this folder extract the first 3 files and place in the user_sync_tool folder.

&#9744; Next, rename the 3 config example files by removing the leading "1 ", "2 ", and "3 " from the names.  We will edit these files to create the real User Sync configuration files.



![install2](images/install_config_files.png)


[Previous Section](identify_server.md) \| [Back to Contents](index.md) \| [Next Section](setup_config_files.md)
