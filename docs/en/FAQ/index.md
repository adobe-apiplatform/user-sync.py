---
layout: page
title: User Sync Frequently Asked Questions
advertise: FAQ
lang: en
nav_link: FAQ
nav_level: 1
nav_order: 500
---
### Table of Contents
{:."no_toc"}

* TOC Placeholder
{:toc}


### What is User Sync?

A tool that will enable enterprise customers to create/manage Adobe 
users and entitlement assignments utilizing Active Directory (or other 
tested OpenLDAP directory services).  The target users are IT Identity
Administrators (Enterprise Directory / System Admins) who will be able 
to install and configure the tool.  The open-source tool is customizable 
so that customers can have a developer modify it to suit their own 
particular requirements. 

### Why is User Sync important?

The cloud-agnostic (CC, EC, DC) User Sync tool serves as a catalyst 
to move more users to named user deployment, and fully take advantage 
of the products and services capabilities within the Admin Console.
 
### How does it work?

When User Sync runs, it fetches a list of users from the organization’s 
Active Directory (or other data source) and compares it with the list of 
users within the Admin Console.  It then calls the Adobe User Management 
API so that the Admin Console is synchronized with the organization’s 
directory.  The change flow is entirely one-way; any edits made in the 
Admin Console do not get pushed out to the directory.

The tools allows the system admin to map user groups in the customer’s 
directory with product configuration and user groups in the Admin Console

To set up User Sync, the organization needs to create a set of credentials 
in the same way they would to use the User Management API.
 
### Where do I get it?

User Sync is open source, distributed under the MIT License, and maintained by Adobe. It is available [here](https://github.com/adobe-apiplatform/user-sync.py/releases/latest).


### Does user sync apply for both on-premise and Azure Active Directory servers?

User sync supports local or Azure hosted AD (Active Directory) servers as well as any other LDAP servers.  It can also be driven from a local file.

### Is AD treated as an LDAP server?

Yes, AD is accessed via the LDAP v3 protocol, which AD fully supports.

### Does User Sync automatically put all my LDAP/AD user groups into the Adobe Admin Console?

No.  In those cases 
where the groups on the enterprise side correspond to desired product access 
configurations, the User Sync configuration file can be set up to map 
users to Product Configurations (PCs) or User Groups on the Adobe 
side based on their enterprise-side group membership.  User groups and Product Configurations must be set up manually in the Adobe Admin Console.

 
### Can User Sync be used to manage the membership in User Groups or just Product Configurations?

In User Sync, you can use user groups or Product Configurations in the mapping from directory groups.  So users can be added to or removed from user groups as well as PCs.  You can't create new user groups or product configurations however; that must be done in the Admin Console.

### In the examples in the user manual I see that each directory group is mapped to exactly one Adobe group; is it possible to have 1 AD group map to multiple product configurations?

Most of the examples show just a single Adobe user group or PC, but the mapping can be one to many.  Simply list all the user groups or PCs, one per line, with a leading "-" (and indented to the proper level) on each as per YML list format.

### Can the UMAPI server's throttling interfere with the operation of user sync?

No, User sync handles throttling and retries so that throttling may slow 
down the overall user sync process, but there is no problem caused by throttling 
and user sync will properly complete all operations.

The Adobe systems protect themselves from overload by tracking the incoming 
request volume.  If this is starting to exceed limits, then requests return 
a "retry-after" header indicating when capacity will be available again.  User sync honors these headers and waits for the requested amount of time before retrying.  More information, including code samples, can be found in the [User Management API documentation](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/gettingstarted.html).
 
###  Is there a local list of users created/updated (on the user sync side) in order to reduce Adobe server calls?

User sync always queries the Adobe user management systems to get 
current information when it is run, except as follows.  There is an option available in 
User Sync release 2.2 or later to prevent this query and push updates to Adobe without
regard to the current state of users in Adobe's user management system. If you can determine
which users have changed in the local directory, and are confident that other users 
have not been altered on the Adobe side, this approach can shorten the run time 
(and network usage) of your sync jobs.
 
### Is the user sync tool limited to federated Ids or can any type of ID can be created?

User sync supports all id types (Adobe IDs, Federated IDs and Enterprise IDs).

### An Adobe organization can be granted access to users from domains owned by other organizations.  Can User Sync handle this case?

Yes.  User Sync can both query and manage user 
group membership and product access for users in both owned and accessed domains.  However, 
like the Admin Console, User Sync can only be used to create and update user 
accounts in owned domains, not domains owned by other organizations.  Users from those
domains can be granted product access but not edited or deleted.

### Is there an update function, or just add/remove users (for only federatedID)?

For all types of ID (Adobe, Enterprise, and Federated), User Sync supports 
update of group memberships under control of the --process-groups option.  
For Enterprise and Federated IDs, User Sync supports update of first name, last 
name, and email fields under control of the --update-user-info  option.  When 
country updates become available in the Admin Console, they will also be 
available via the UMAPI.  And for Federated IDs whose "User Login Setting" 
is "Username", User Sync supports update of username as well as the other fields.

### Is the user sync tool dedicated to a particular OS?

User Sync is an open source python project.  Users can build for any OS platform they desire.  We provide builds for Windows, OS X, Ubuntu, and Cent OS 7 platforms.

### Has this been tested on python 3.5?

User Sync has been run successfully on Python 3.x.  We started development with 2.7 but most work is now on the Python 3.6.x series and Python 3 builds are available for recent releases.  Feel free to report problems (and contribute fixes) to the open source site at https://github.com/adobe-apiplatform/user-sync.py.

### If something changes in the API (new field in creating users, for example ) how will the update  be applied to the user sync tool?

User sync is an open source project.  Users can download and build the latest 
sources at their discretion.  Adobe will post new releases with builds periodically.  
Users can stay informed of them via git notifications.  When adopting a new release, 
only the single pex file needs to be updated by the user.  If there are configuration 
changes or command line changes to support new features, there may be updates in 
those files to take advantage of them.

Also note that User Sync is built on top of umapi-client, which is the only module with direct knowledge of the API. When the API changes, umapi-client always gets updated to support it. If and when API changes provide for more User Sync-related capabilities, then User Sync may be updated to provide them.

### Does User sync need some sort of whitelisting with the firewall rules of the machine on which it runs?

Generally no. User sync is purely a network client, and does not accept incoming connections, so the machine-local firewall rules for inbound connections are irrelevant.

However, as a network client, User Sync requires SSL (port 443) outbound access through customer network firewalls in order to reach the Adobe servers. Customer networks also need to permit User Sync, if configured that way, to reach the customer LDAP/AD server, on whatever port is specified in the User Sync configuration (port 389 by default).

### Is User Sync part of Adobe's offering to EVIP customers?
 
Yes, all Enterprise customers have access to the UMAPI and User Sync, regardless of their buying program (E-VIP, ETLA, or Enterprise Agreement).
 
### What is the internationalization story for the User Sync tool;  is it internationally enabled (support at least double-byte character input)?
 
Earlier versions of User Sync were erratic in their support for international 
character data, although they worked fairly reliably with utf8-encoded data 
sources. As of version 2.2, User Sync is fully Unicode-enabled, and can accept 
configuration files and directory or spreadsheet data sources that use any 
character encoding whatever (with a default expectation of utf8).

