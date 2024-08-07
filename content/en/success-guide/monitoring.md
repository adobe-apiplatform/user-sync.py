---
weight: 250
type: docs
title: Monitoring
---

# Monitoring the User Sync Process

If you are using User Sync as an ongoing process, you’ll need to identify
someone who can monitor and maintain the User Sync process. You'll also want to
set up some automated monitoring mechanism to make it easy to see what is going
on and determine if any errors have occurred.

There are several possible approaches to monitoring:

- Inspect log files from when User Sync runs
- Email latest run log summary to administrators who watch emails for errors (or
  non-delivery)
- Hook log files to a monitoring system and setup notifications for when errors
  occur

For this step, you need to identify who will be responsible for User Sync
operation and identify how monitoring will be set up.

Identify the person or team responsible for monitoring and make sure they are up
to speed on User Sync and what it is doing.

If you have a log analysis and alerting system available, arrange for the log
from User Sync to be sent to the log analysis system and set up alerts if any
Error or Critical messages appear in the log. You may also want to alert on
Warning messages.
