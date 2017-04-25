# User Sync Frequently Asked Questions (FAQ)

**Q: What is User Sync?**<br/>
A: A tool that will enable enterprise customers to create/manage Adobe 
users and entitlement assignments utilizing Active Directory (or other 
tested OpenLDAP directory services).  The target users are IT Identity
Administrators (Enterprise Directory / System Admins) who will be able 
to install and configure the tool.  The open-source tool is customizable 
so that customers can have a developer modify it to suit their own 
particular requirements. 

**Q: Why is User Sync important?**<br/>
A: The cloud-agnostic (CC, EC, DC) User Sync tool serves as a catalyst 
to move more users to named user deployment, and fully take advantage 
of the products and services capabilities within the Admin Console.
 
**Q: How does it work?**<br/>
A: When User Sync runs, it fetches a list of users from the organization’s 
Active Directory (or other data source) and compares it with the list of 
users within the Admin Console.  It then calls the Adobe User Management 
API so that the Admin Console is synchronized with the organization’s 
directory.  The change flow is entirely one-way; any edits made in the 
Admin Console do not get pushed out to the directory.

The tools allows the system admin to map user groups in the customer’s 
directory with product configuration and user groups in the Admin Console

To set up User Sync, the organization needs to create a set of credentials 
in the same way they would to use the User Management API.
 
**Q: Where do I get it?**<br/>
A: User Sync will be distributed through the Adobe public Github repo here:
https://github.com/adobe-apiplatform/user-sync.py/releases/latest

**Q: Does user sync apply for local AD version and not Azure one?**<br/>
A: User sync supports local or Azure hosted AD (Active Directory) servers as well as any other LDAP servers.  It can also be driven from a local file.

**Q: Is there something ongoing for the Azure AD version?** Would it do 
functionally something different than this one or just create/remove 
users from AD designated groups?<br/>
A: Adobe is working on additional features to integrate with Azure 
AD services.  Watch for announcements of new features in this area in the future.

**Q: Is AD treated as an LDAP server?**<br/>
A: Yes, AD is accessed through python using the openLDAP package.

**Q: In setting up user sync must there be a configuration match between 
AD groups and Product Configuration from Admin Console?**<br/>
A: No.  It's possible to use User Sync just to get the users over to the 
Adobe side (including just specific groups of users).  But in those cases 
where the groups on the enterprise side correspond to desired product access 
configurations, the User Sync configuration file can be set up to map 
users to Product Configurations (PCs) or User Groups on the Adobe 
side based on their enterprise-side group membership.

**Q: With the API and manually in the Admin Console(AC) is it possible to 
add users to Groups in the AC?** The group can have one or more Product 
Configurations associated.<br/>
A: Yes.  Once you have set up your PCs and User Groups in the Admin Console, 
you can use either the UMAPI or manual processes to add people to those groups.
User Sync, of course, will also add the users to PCs and User Groups.
 
**Q: Is there a way to declare Groups also or just Product Configurations**
(ex: group A from AD is a match to group A in AC also, created in advance 
by the admin of the org)<br/>
A: In User Sync, you can use user groups or Product Configurations in the mapping from directory groups.  So users can be added to user groups and/or PCs.

**Q: In the documentation I see that there is a 1:1 match (1 AD group = 1 product 
configuration); is it possible to have 1 AD group and multiple product 
configurations?** How about 1 AD group vs many AC groups?<br/>
A: Most of the examples show just a single Adobe user group or PC, but the mapping can be one to many.  Simply list all the user groups or PCs, one per line, with a leading "-" (and indented to the proper level) on each as per YML list format.

**Q: I understand the user sync tool would do a GET users from the org (or product 
configuration?) in order to compare with the extract of users from AD. It is 
known the limitation of number of requests per minute to our server.  Is this 
a problem?**  For example,  the back-off can stop the activity to query or update 
in X number of tries. This can leave a partially updated list of users or a 
partial query.<br/>
A: No, User sync handles throttling and retries so that throttling may slow 
down the overall user sync process, but there is no problem caused by throttling 
and user sync will properly complete all operations.
 
**Q:  Is there a local list of users created/updated (on the user sync side) 
in order not to disturb our server every time for a list of users from the 
org/product configuration?**<br/>
A: No, User sync always queries the Adobe user management systems to get 
current information when it is run.

**Q: I’d like to know more on how the user sync tool deals with the throttling 
in general.**<br/>
A: The Adobe systems protect themselves from overload by tracking the incoming 
request volume.  If this is starting to exceed limits, then requests return 
a "retry-after" header indicating when capacity will be available again.  User sync honors these headers and waits for the requested amount of time before retrying.  More information, including code samples, can be found in the User Management API documentation at https://www.adobe.io/apis/cloudplatform/usermanagement/docs/throttling.html.
 
**Q: Is the user sync tool dedicated for federated Ids or any type of ID can be 
created?**<br/>
A: User sync supports all id types (Adobe IDs, Federated IDs and Enterprise IDs).

**Q: An org can have owned domains and domains to which another org has granted it 
access. The UM API can run queries on both. How about user sync? Users are 
added to the product configuration just because they are found in the AD group, 
no check on the domain?**<br/>
A: User Sync uses the UMAPI, so it can both query and manage the user 
groups and product access for users in both owned and accessed domains.  However, 
like the Admin Console, User Sync can only be used to create and update user 
accounts in owned domains, not domains owned by other organizations.

**Q: Is there an update function, or just add/remove users (for only 
federatedID)?**<br/>
A: For all types of ID (Adobe, Enterprise, and Federated), User Sync supports 
update of group memberships under control of the --process-groups option.  
For Enteprise and Federated IDs, User Sync supports update of first name, last 
name, and email fields under control of the --update-user-info  option.  When 
country updates become available in the Admin Console, they will also be 
available via the UMAPI.  And for Federated IDs whose "User Login Setting" 
is "Username", User Sync supports update of username as well as the other fields. 

**Q: The user sync tool is dedicated to a particular OS?** (for example, win package 
is different than unix or linux installer?)<br/>
A:  User Sync is an open source python project.  Users can build for any OS platform they desire.  We provide builds for Windows, OS X, Ubuntu, and Cent OS 7 platforms.
 
**Q: Has this been tested on python 3.5?**<br/>
A: User Sync has been run successfully on Python 3.x, but most of our use and testing is on Python 2.7 so you may discover problems, and we only provide builds on Python 2.7.  Feel free to report (and contribute fixes) to the open source site at https://github.com/adobe-apiplatform/user-sync.py.

**Q: If something changes in the API (new field in creating users, for example ) how will the update  be applied to the user sync tool?** New package or python modules can be directly modified customer side?<br/>
A: User sync is an open source project.  Users can download and build the latest 
sources at their discretion.  Adobe will post new releases with builds periodically.  
Users can stay informed of them via git notifications.  When adopting a new release, 
only the single pex file needs to be updated by the user.  If there are configuration 
changes or command line changes to support new features, there may be updates in 
those files to take advantage of them.

**Q: Does User sync need some sort of whitelisting with the firewall rules of the machine
on which it runs?** I see Windows users are more prone to such errors, from support 
experience.<br/>
A: User sync needs to be able to access the enterprise directory system and Adobe.  
Since there can be significant variance across system setups, we can't give any 
specific steps.  LDAP typically uses port 389, but can be configured by IT.  Adobe 
only requires REST calls over SSL on port 443.

**Q: There is something specified about a second step in differentiating the users 
of a bigger company by adding the country code and the cost centre as metadata 
to users when they are created; is user sync set up with this feature or not 
this version?**<br/>
A: Country is required for Federated Ids and useful for Enterprise Ids (if not 
supplied, the user will have to supply the country on first login).  User Sync 
supports using the standard control field from LDAP, and also supports the 
specification of a default country code to be used.  
User Sync can also be customized to call a customer-provided python "hook" in the 
User Sync configuration; this hook can use customer-side attributes such as 
cost center to control attributes and group mappings of users on the Adobe side.
 
**Q: Is User Sync part of Adobe's offering to EVIP customers as well as ETLA customers?** 
Or to put it another way, do EVIP customers have access to the UM API?<br/>
A: Yes, EVIP customers have access to the UMAPI and User Sync.
 
**Q: What is the Internationalization story for the User Sync tool;  is it 
internationally enabled (support at least double-byte character input)?** <br/>
A:  Python 2.7 (the language of the tool) distinguishes “str” (8-bit character strings) 
and “unicode” (enforced UTF-8-encoded 8 bit character strings), and the user 
sync code uses “str” not “unicode” everywhere.  However, all of the output of 
the tools are UTF-8 encoded, and as long as UTF-8 encoding is used on the 
input things should work fine.  This has been lightly tested and no problems were 
found.  Further testing is planned.

We have an enhancement planned to port the tool to run in Python 3 as well as Python 2.  
At that point we can be assured that unicode will work fine, as the types are merged 
in Python 3.  Customers for whom this is critical should build using Python 3.
 
 
