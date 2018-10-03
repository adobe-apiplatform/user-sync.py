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


### Without Email Notification:
Create a ps1 script with the invocation of user-sync. Create the file run_sync.ps1 with contents below:

	python .\user-sync.pex --users mapped --process-groups


### With Email Notification:
Create the following PowerShell file with the invocation of user-sync piped to a scan to pull out relevant log entries for a summary.  Create the file run_sync.ps1 with contents below::

```powershell
<#
Run the following command to Export SMTP Server Credential to XML
Exported Credential file is user profile based.
Must export under the same account that script will be running under

Get-Credential | Export-Clixml .\email_cred.xml
#>

#Run UST and Save console output to a variable. Modify this according your UST command

$outputCMD = python .\user-sync.pex --users mapped --process-groups
# Filter for Warning, Error or Critical Error message from Console Output
$err = $outputCMD | Select-String -Pattern 'WARNING','ERROR','CRITICAL'
#Specify temporary log filename for email attachment.
$outputFileName = 'ust_output.log'
if ($err) {
    #Temporary export console output to a log file
    $outputCMD | Out-File $outputFileName
    $emailSettings = @{
        #Set the following to your SMTP Relay Server
        SmtpServer = 'smtp.office365.com'
        #Set your SMTP Relay Server port #
        Port = 587
        #If your SMTP server required SSL, set this to $true else remove this setting.
        UseSSL = $true
        #If your SMTP server required Authentication. You must specified Credential in PSCredential object
        Credential = Import-Clixml .\email_cred.xml
        #Email To
        To = 'DL-IT-Status@example.com'
        #Email From
        From = 'SVCUST@example.com'
        #Email Subject
        Subject = "ERROR! - UST Sync Error - $((Get-Date).ToString('g'))"
        #Body of the email will display the error messages
        Body = "$err"
        #Temp Log output file will be attach to the email
        Attachment = $outputFileName
    }
    #Send the email with the specified settings above
    Send-MailMessage @emailSettings
    #Clean up temp log output
    Remove-Item $outputFileName -Force
}
```

### Task Scheduler
Using Windows Task Scheduler PowerShell cmdlets below to schedule User Sync Tool to run every day starting at 11:00 PM:

Edit the following and invoke the commands from PowerShell with elevated privileges.

-WorkingDirectory with your User-Sync Directory path<br/>
-User with an account that will be running the Task<br/>
-Password with an account password

```powershell
$Trigger= New-ScheduledTaskTrigger -At 11:00PM -Daily
$Action= New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File run_sync.ps1" -WorkingDirectory "[user-sync-directory]"
Register-ScheduledTask -TaskName "Adobe User Sync" -Trigger $Trigger -User "[UserName Here]" -Password "[Password Here]" -Action $Action -RunLevel Highest –Force
```

[Check the documentation on the windows task scheduler for more details](https://docs.microsoft.com/en-us/powershell/module/scheduledtasks)

Note that often when setting up scheduled tasks, commands that work from the command line do not work in the scheduled task because the current directory or user id is different.  It is a good idea to run one of the test mode commands (described in the "Make a Test Run" section) the first time you try the scheduled task.


## Setting Up Scheduled Run on Unix-Based Systems

### Without Email Notification:
Create a shell script with the invocation of user-sync. Create the file run_sync.sh with contents below:

	cd [user-sync-directory-path]
	./user-sync --users mapped --process-groups

### With Email Notification:
Create a shell script with the invocation of user-sync piped to a scan to pull out relevant log entries for a summary.  Create the file run_sync.sh with contents below:

	cd [user-sync-directory-path]
	./user-sync --users mapped --process-groups |  grep "CRITICAL\\|WARNING\\|ERROR\\|=====\\|-----\\|number of\\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`”
    Your_admin_mailing_list@example.com

You need to fill in your specific User Sync command line options and the email address to which the report should be sent.

### Cron Job
This entry in the Unix crontab will run the User Sync tool at 11 PM each day:

	0 23 * * *  path_to_Sync_shell_command/run_sync.sh

Cron can also be setup to email results to a specified user or mailing list.  Check the documentation on cron for you Unix system for more details.

Note that often when setting up scheduled tasks, commands that work from the command line do not work in the scheduled task because the current directory or user id is different.  It is a good idea to run one of the test mode commands (described in the "Make a Test Run" section) the first time you try the scheduled task.


[Previous Section](command_line_options.md) \| [Back to Contents](index.md)

