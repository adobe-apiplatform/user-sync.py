---
layout: default
lang: en
nav_link: Scheduling
nav_level: 2
nav_order: 320
---

# Setup Scheduled Ongoing Execution of User Sync


[Previous Section](command_line_options.md) \| [Back to Contents](index.md) 

## Setting Up Scheduled Run on Windows

First, create a batch file with the invocation of user-sync piped to a scan to pull out relevant log entries for a summary.  Create the file run_sync.bat for this with contents like:

	cd user-sync-directory
	python user-sync.pex --users file example.users-file.csv --process-groups | findstr /I "==== ----- WARNING ERROR CRITICAL Number" > temp.file.txt
	rem email the contents of temp.file.txt to the user sync administration
	your-mail-tool –send file temp.file.txt


There is no standard email command-line tool in Windows, but several are available commercially.
You need to fill in your specific command line options.

This code uses the Windows task scheduler to run the User Sync tool every day starting at 4:00 PM:

	C:\> schtasks /create /tn "Adobe User Sync" /tr path_to_bat_file/run_sync.bat /sc DAILY /st 16:00

Check the documentation on the windows task scheduler (help schtasks) for more details.

Note that often when setting up scheduled tasks, commands that work from the command line do not work in the scheduled task because the current directory or user id is different.  It is a good idea to run one of the test mode commands (described in the "Make a Test Run" section) the first time you try the scheduled task.


## Setting Up Scheduled Run on Unix-Based Systems

First, create a shell script with the invocation of user-sync piped to a scan to pull out relevant log entries for a summary.  Create the file run_sync.sh for this with contents like:

	cd user-sync-directory
	./user-sync --users file example.users-file.csv --process-groups |  grep "CRITICAL\\|WARNING\\|ERROR\\|=====\\|-----\\|number of\\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” 
    Your_admin_mailing_list@example.com


You need to fill in your specific User Sync command line options and the email address to which the report should be sent.

This entry in  the Unix crontab will run the User Sync tool at 4 AM each day: 

	0 4 * * *  path_to_Sync_shell_command/run_sync.sh 

Cron can also be setup to email results to a specified user or mailing list.  Check the documentation on cron for you Unix system for more details.

Note that often when setting up scheduled tasks, commands that work from the command line do not work in the scheduled task because the current directory or user id is different.  It is a good idea to run one of the test mode commands (described in the "Make a Test Run" section) the first time you try the scheduled task.


[Previous Section](command_line_options.md) \| [Back to Contents](index.md) 

