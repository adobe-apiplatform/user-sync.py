---
title: Introduction
type: docs
bookToc: true
---

# Adobe User Sync

User Sync is a command-line tool that moves user and group information from your
organization's enterprise directory system (such as an Active Directory or other
LDAP system) to your organization's directory in the Adobe Admin Console.

Each time you run User Sync, it looks for differences between the user and group
information in the two systems, and updates the Adobe directory to match the
information in your directory.

{{< columns >}}
## Setup and Success Guide

The fastest way to get started with User Sync is to read the [Setup and Success
Guide]({{< ref "success-guide" >}}), which gives step-by-step instructions for
setting up the needed configuration files and running the tool.

<--->

## User Manual

For all the details of using User Sync, including how to set it up for a number
of different typical usage scenarios, dive into the [User Manual]({{< ref
"user-manual" >}}). It's also your starting point for customizing the behavior
of User Sync, as it includes instructions for doing custom mappings between
customer directory information and data on the Adobe side.

<--->

## Frequently Asked Questions 

We have compiled a [FAQ document]({{< ref "faq" >}}) that answers many questions we
have been asked and others we expected to be asked.
{{< /columns >}}
