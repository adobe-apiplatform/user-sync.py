# Sign Sync v1.0
Sign Sync allows for an automated process of moving users over from Admin Console into your Adobe Sign. 
Sign Sync works as an addition add on feature to the Adobe User Sync Tool, which allows you to synchronize entities within 
your LDAP over to Adobe Admin Console. Once users are assigned into Adobe Admin Console with Sign entitlements, 
Sign Sync will locate users with Sign entitlements and sync them over to Adobe Sign.

Full detailed <a href="https://github.com/NathanNguyen345/user-sync.py/blob/v2/user_sync/sign_sync/Sign%20Sync%20User%20Guide.docx">
User Guide</a> can be found here.

## Disclaimer
Sign Sync works as a one-way sync from Adobe Admin Console to Adobe Sign. Any changes made in Adobe Sign such as group 
creation, user creation, privileges, or moving users to different groups will be reverted back to the current state in 
Admin Console. Changes should be made either from your LDAP or Admin Console depending how you have your mapping set up.

## Prerequisites
This is a list of all prerequisites that you should checked off to verify that you have what is needed to start the 
deployment process. Please make sure you have all the prerequisites set up before using Sign Sync.

Prerequisites | Description
------------- | -----------
Python 3.7 | Python version 3.7 is recommended as the User Sync Tool 2.3 is running <a href="https://www.python.org/downloads/release/python-370/">Python 3.7</a>
Adobe Sign Integration Key | The integration key to your <a href="https://secure.echosign.com/public/login">Adobe Sign.</a>
Text Editor | This will be required to edit any configuration files.

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
for User Sync Tool. If so, you should be able to perform a 
<a href="https://adobe-apiplatform.github.io/user-sync.py/en/success-guide/test_run.html">test run</a>. Once a successful 
run of User Sync Tool is confirmed, you can start configuring the Sign Sync feature into User Sync Tool.
