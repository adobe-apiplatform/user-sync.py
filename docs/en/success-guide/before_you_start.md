---
layout: default
lang: en
nav_link: Create Apps
nav_level: 2
nav_order: 10
---

# What You Need To Know Before You Start

[Back to Contents](index.md) \| [Next Section](layout_orgs.md)

## Introduction to User Sync

Adobe User Sync is a command-line tool that moves user and group information from your organization's  enterprise directory system (such as Active Directory or other LDAP system) or other sources to the Adobe User Management system.  User Sync is predicated on the notion that the enterprise directory system is the authoritative source of information on users and user information from it is moved into the Adobe User Management System under control of a set of user sync configuration files and command line options.

Each time you run the tool it looks for differences between the user information in the two systems, and updates the Adobe system to match the enterprise directory.

Using User Sync, you can cause the creation of new Adobe accounts when new users appear in the directory, update of account information when certain fields in the directory change, update user group and Product Configuration (PC) membership to control allocation of licenses to users.  You can also manage deletion of Adobe accounts when the user is removed from the enterprise directory.

There are also capabilities to use custom directory attributes to control values that go into the Adobe account.

In addition to syncing with enterprise directory systems, it is also possible to sync with a simple csv file.  This may be useful for small organizations or departments that do not run centralized managed directory systems.

Finally, for those with large directories, it is possible to drive user sync via push notifications of changes in the directory system, rather than doing comparisons of large numbers of user accounts.

## Terminology

- User Group: a named group of users in the Adobe user management system
- PC: a Product Configuration.  An Adobe group-like mechanism where, when users are added to the PC, they are granted access to a specific Adobe product.
- Directory: a general term for a user directory system such as Active Directory(AD), LDAP, or a csv file listing users
- Directory group: a named group of users in the directory

 

## Range of Configurations
User sync is a very general tool that can accommodate a wide variety of configurations and process needs.

Depending on your organization size and what Adobe products you have purchased you will likely have one or more Administrative Consoles and organizations in your Adobe setup.  Each organization has an administrator or administrators and you must be one of them to set up access credentials for user sync.

Each Adobe organization has a set of users.  Users may be one of three type:

- AdobeId: an account created and owned by the user.  The account and access to it are managed using Adobe facilities.  An administrator cannot control the account.

- Enterprise Id: an account created and owned by the company.  The account and access to it are managed using Adobe facilities.  An administrator can control the account.

- Federated Id: an account created and owned by the company.  The account is partially managed using Adobe facilities, but access (password and login) is controlled and operated by the company.

Enterprise and Federated Ids must be in a domain that is claimed and owned by the company and is set up in the Adobe organization using the Adobe Admin Console.

If you have more than one Adobe organization, you will need to understand which domains and users are in which organizations and how those groups correspond to the accounts defined by your directory system.  You may have a simple configuration with a single directory system and a single Adobe organization.  If you have more than one, of either, you will need to draw a map of which systems are sending user information to which Adobe organizations.  There may need to be multiple user sync instances, each targeting a different Adobe organization.

User Sync can handle user creation and update as well as license management.  Using User Sync for license management is optional and independent of other User Sync functions.  License management can be handled manually using the Adobe Admin Console, or via some other application.

There are a variety of options available for handling account deletion.  You may wish Adobe accounts to be deleted immediately when the corresponding enterprise account is removed, or you may have some other process in place to leave the Adobe account until someone checks if there are assets in that account to be recovered.  User Sync can handle a range of deletion processes including these.


## User Sync runs on your systems.  
You’ll need a server on which to host it.  User Sync is a Python application and is open source.  You can use a pre-build Python package or build it yourself from source.

## What you will need to know and do

----------

### Directory System
You’ll need to understand your directory and how to access it.

You’ll need to understand which users in the directory should be Adobe users.

### Process Issues
You’ll need to establish an ongoing process and have someone to monitor it.

You’ll need to understand how products are to be managed (who gets access and how, for example) in your company

You’ll need to decide if you will manage just users, or users and product licenses.

You’ll need to decide how you want to handle account deletion when users are removed from the directory.

### Adobe environment
You’ll need a good understanding of what Adobe products you have

You’ll need to understand what Adobe organizations are setup and which users go into which organizations.

You’ll need administrative access to your Adobe organization(s)

[Back to Contents](index.md) \|  [Next Section](layout_orgs.md)
