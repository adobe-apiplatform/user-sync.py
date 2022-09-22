---
layout: default
lang: en
nav_link: Monitoring
nav_level: 2
nav_order: 300
---

# Monitoring the User Sync Process

[Previous Section](test_run.md) \| [Back to Contents](index.md) \| [Next Section](command_line_options.md)

If you are using User Sync as an ongoing process, you’ll need to identify someone who can monitor and maintain the User Sync process.  You'll also want to set up some automated monitoring mechanism to make it easy to see what is going on and determine if any errors have occurred.

There are several possible approaches to monitoring:

- Inspect log files from when User Sync runs
- Email latest run log summary to administrators who watch emails for errors (or non-delivery)
- Hook log files to a monitoring system and setup notifications for when errors occur

For this step, you need to identify who will be responsible for User Sync operation and identify how monitoring will be set up.

&#9744; Identify the person or team responsible for monitoring and make sure they are up to speed on User Sync and what it is doing.

&#9744; If you have a log analysis and alerting system available, arrange for the log from User Sync to be sent to the log analysis system and set up alerts if any Error or Critical messages appear in the log.  You may also want to alert on Warning messages.

[Previous Section](test_run.md) \| [Back to Contents](index.md) \| [Next Section](command_line_options.md)
