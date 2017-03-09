## Monitoring the User Sync Process

[Previous Section](test_run.md) | [Back to Contents](Contents.md) |  [Next Section](command_line_options.md)

If you are using user-sync as an ongoing process, you’ll need to identify someone who can monitor and maintain the user sync process.  You'll also want to set up some automated monitoring mechanism to make it easy to see what is going on and determine if any errors have occurred.

There are several possible approaches to monitoring:

- Inspect log files from when user sync runs
- email latest run log summary and recipients watch emails for errors (or non-delivery)
- hook log files to a monitoring system and setup notifications for when errors occur

For this step, you need to identify who will be responsible for user sync operation and identify how monitoring will be set up.

&#9744; Identify the person or team responsible for monitoring and make sure they are up to speed on user sync and what it is doing.

&#9744; If you have a log analysis and alerting system available, arrange for the log from user sync to be sent to the log analysis system and set up alerts if any Error or Critical messages appear in the log.  You may also want to alert on Warning messages.

[Previous Section](test_run.md) | [Back to Contents](Contents.md) |  [Next Section](command_line_options.md)
