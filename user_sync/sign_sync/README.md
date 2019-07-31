# Sign Sync v0.2.0
Sign Sync allows for an automated process of moving users over from Admin Console into your Adobe Sign. 
Sign Sync works as an addition add on feature to the Adobe User Sync Tool, which allows you to synchronize entities within 
your LDAP over to Adobe Admin Console. Once users are assigned into Adobe Admin Console with Sign entitlements, 
Sign Sync will locate users with Sign entitlements and sync them over to Adobe Sign.

Full detailed [User Guide](USER_GUIDE.md) can be found here.

## Disclaimer
Sign Sync works as a one-way sync from Adobe Admin Console to Adobe Sign. Any changes made in Adobe Sign such as group 
creation, user creation, privileges, or moving users to different groups will be reverted back to the current state in 
Admin Console. Changes should be made either from your LDAP or Admin Console depending how you have your mapping set up.

## Prerequisites

* Python 3.6 ([download link](https://www.python.org/downloads/release/python-368/))
* Adobe Sign Integration Key
* Text Editor ([Notepad++](https://notepad-plus-plus.org/) is recommended for Windows)

## Features
The following features are available in version 1.0 of Sign Sync.

Sign Sync Features | Description
-------------------| -----------
Group Creation | New groups created in Admin Console will be synced over to the Sign Console.
User Privileges | User privileges set in Admin Console will sync over to Sign Console.
Ignore Groups | Ability to ignore specific groups defined in a configuration file.
Ignore Admin Privileges | Ability to ignore specific admin roles to be synced over in Sign.

## Deployment
Sign Sync works alongside Adobe User Sync Tool. Please make sure that all dependencies and packages are set up correctly 
for User Sync Tool. If so, you should be able to perform a [test run](https://adobe-apiplatform.github.io/user-sync.py/en/success-guide/test_run.html).
Once a successful run of User Sync Tool is confirmed, you can start configuring the Sign Sync feature into User Sync Tool.
