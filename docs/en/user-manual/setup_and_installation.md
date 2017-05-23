---
layout: default
lang: en
nav_link: Setup and Installation
nav_level: 2
nav_order: 20
---

# Setup and Installation

[Previous Section](index.md)  \| [Next Section](configuring_user_sync_tool.md)

## In This Section
{:."no_toc"}

* TOC Placeholder
{:toc}

---

The use of the User Sync tool depends on your enterprise having
set up product configurations in the Adobe Admin
Console. For more information about how to do this, see the
[Configure Services](https://helpx.adobe.com/enterprise/help/configure-services.html#configure_services_for_group)
help page.

## Set up a User Management API integration on Adobe I/O

The User Sync tool is a client of the User Management API. Before
you install the tool, you must register it as a client of the API
by adding an *integration* in the Adobe I/O
[Developer Portal](https://www.adobe.io/console/). You will need
to add an Enterprise Key integration in order to obtain the
credentials the tool needs to access the Adobe User Management
system.

The steps required for creating an integration are described in
detail in the
[Setting up Access](https://www.adobe.io/apis/cloudplatform/usermanagement/docs/setup.html)
section of the Adobe I/O User Management API website.  The
process requires that you create an integration-specific
certificate, which may self-signed.  When the process is
complete, you will be assigned an **API key**, a **Technical
account ID**, an **Organization ID**, and a **client secret**
that the tool will use, along with your cerficate information, to
communicate securely with the Admin Console. When you install the
User Sync tool, you must provide these as configuration
values that the tool requires to access your organization's user
information store in Adobe.

## Set up product-access synchronization

If you plan to use the User Sync tool to update user access to
Adobe products, you must create groups in your own enterprise
directory that correspond to the user groups and product
configurations that you have defined in the
[Adobe Admin Console](https://www.adobe.io/console/). Membership
in a product configuration grants access to a particular set of
Adobe products. You can grant or revoke access to users or to
defined user groups by adding or removing them from a product
configuration.

The User Sync tool can grant product access to users by adding
users to user groups and product configurations based on their
enterprise directory memberships, as long as the group names are
correctly mapped and you run the tool with the option to process
group memberships.

If you plan to use the tool in this way, you must map your
enterprise directory groups to their corresponding Adobe groups
in the main configuration file. To do this, you must ensure that
the groups exist on both sides, and that you know the exact
corresponding names.

### Check your products and product configurations

Before you start configuring User Sync, you must know what Adobe
products your enterprise uses, and what product
configurations and user groups are defined in the Adobe User
Management system. For more information, see the help page for
[configuring enterprise services](https://helpx.adobe.com/enterprise/help/configure-services.html#configure_services_for_group).

If you do not yet have any product configurations, you can use the
Console to create them. You must have some, and they must have
corresponding groups in enterprise directory, in order to
configure User Sync to update your user entitlement information.

The names of product configurations generally identify
the types of product access that users will need, such as All
Access or Individual Product Access. To check the exact names, go
to the Products section in the
[Adobe Admin Console](https://www.adobe.io/console/) to see the
products that are enabled for your enterprise. Click a product to
see the details of product configurations that have been
defined for that product.

### Create corresponding groups in your enterprise directory

Once you have defined user groups and product configurations in
the Adobe Admin Console, you must create and name corresponding
groups in your own enterprise directory. For example, a directory
group corresponding to a “All Apps” product configuration
might be called “all_apps”.

Make a note of the names you choose for these groups, and which
Adobe groups they correspond to. You will use this to set up a
mapping in the main User Sync configuration file. See details in
the [Configure group mapping](configuring_user_sync_tool.md#configure-group-mapping) section
below.

It is a best practice to note in the description field of the Product Configuration or User Group that the group is managed by User Sync and should not be edited in the Admin Console.

![Figure 2: Group Mapping Overview](media/group-mapping.png)

## Installing the User Sync tool

### System requirements

The User Sync tool is implemented using Python, and requires
Python version 2.7.9 or higher. For each environment in which you
intend to install, configure and run the script, you must make
sure that Python has been installed on the operating system
before moving to the next step. For more information, see the
[Python web site](https://www.python.org/).

The tool is built using a Python LDAP package, `pyldap`, which in
turn is built on the OpenLDAP client library. Windows Server,
Apple OSX and many flavors of Linux have an OpenLDAP client
installed out of the box.  However, some UNIX operating systems,
such as OpenBSD and FreeBSD do not have this included in the base
installation.

Check your environment to be sure that an OpenLDAP client is
installed before running the script. If it is not present in your
system, you must install it before you install the User Sync
tool.

### Installation

The User Sync Tool is available from the
[User Sync repository on GitHub](https://github.com/adobe-apiplatform/user-sync.py). To
install the tool:

1. Create a folder on your server where you will install the 
User Sync tool and place the configuration files.

1. Click the **Releases** link to locate the latest release,
which contains the release notes, this documentation, sample
configuration files, and all the built versions (as well as
source archives).

2. Select and download the compressed package for your platform
(the `.tar.gz` file). Builds for Windows, OSX, and Ubuntu are
available. (If you are building from source, you can download the
Source Code package that corresponds to the release, or use the
latest source off the master branch.)

3. Locate the Python executable file (`user-sync` or
`user-sync.pex` for Windows) and place it in your User Sync
folder.

4. Download the `example-configurations.tar.gz` archive of sample configuration
files.  Within the archive, there is a folder for “config files –
basic”.  The first 3 files in this folder are required. Other
files in the package are optional and/or alternate versions for
specific purposes. You can copy these to your root folder, then
rename and edit them to make your own configuration files. (See
the following section,
[Configuring the User Sync Tool](configuring_user_sync_tool./md#configuring-the-user-sync-tool).)

5. **In Windows only:**

    Before running the user-sync.pex executable in Windows, you might
need to work around a Windows-only Python execution issue:

    The Windows operating system enforces a file path length limit of
260 characters. When executing a Python PEX file, it creates a
temporary location to extract the contents of the package. If the
path to that location exceeds 260 characters, the script does not
execute properly.

    By default, the temporary cache is in your home folder, which may
cause pathnames to exceed the limit. To work around this issue,
create an environment variable in Windows called PEX\_ROOT, a set
the path to C:\\user-sync\\.pex. The OS uses this variable for
the cache location, which prevents the path from exceeding the
260 character limit.

6. To run the User Sync tool, run the Python executable file,
`user-sync` (or execute `python user-sync.pex` on Windows).

### Security Considerations

Because the User Sync application accesses sensitive information
on both the enterprise and Adobe sides, its use involves a number
of different files that contain sensitive information. Great care
should be take to keep these files safe from unauthorized access.

User Sync release 2.1 or later allow you to store credentials in
the operating system's secure credential store as an alternative
to storing them in files and securing those files, or to store
umapi and ldap configuration files in a secure way that you can
define.  See section [Security recommendations](deployment_best_practices.md#security-recommendations)
for more details.

#### Configuration files

Configuration files must include sensitive information, such as
your Adobe User Management API key, the path to your certificate
private key, and the credentials for your enterprise directory
(if you have one). You must take necessary steps to protect all
configuration files and ensure that only authorized users are
able to access them. In particular: do not allow read access to
any file containing sensitive information except from the user
account that runs the sync process.

If you choose to use the operating system to store credentials,
you still create the same configuration files but rather than storing
the actual credentials, they store key ids that are used to look up
the actual credentials.  Details are shown in
[Security recommendations](deployment_best_practices.md#security-recommendations).

If you are having User Sync access your corporate directory, it
must be configured to read from the directory server using a
service account. This service account only needs read access and
it is recommended that it _not_ be given write access (so that
unauthorized disclousre of the credential does not allow write
access to whomever receives it).

#### Certificate files

The files that contains the public and private keys, but
especially the private key, contain sensitive information. You
must retain the private key securely. It cannot be recovered or
replaced. If you lose it or it is compromised, you must delete
the corresponding certificate from your account. If necessary,
you must create and upload a new certificate. You must protect
these files at least as well as you would protect an account name
and password. The best practice is to store the key files in a
credential management system or use file system protection so
that it can only be accessed by authorized users.

#### Log files

Logging is enabled by default, and outputs all transactions
against the User Management API to the console. You can configure
the tool to write to a log file as well. The files created during
execution are date stamped and written to the file system in a 
folder specified in the configuration file.

The User Management API treats a user’s email address as the
unique identifier. Every action, along with the email address
associated with the user, is written to the log. If you choose to
log data to files, those files contain this
information.

User Sync does not provide any log retention control or
management. It starts a new log file every day.  If you choose to 
log data to files, take necessary
precautions to manage the lifetime and access to these files.

If your company’s security policy does not allow any personally
identifiable information to be persisted on disk, configure the
tool to disable logging to file. The tool continues to output the
log transactions to the console, where the data is stored
temporarily in memory during execution.

## Support for the User Sync tool

Adobe Enterprise customers can use their normal support channels to
get support for User Sync.

Since this is an open source project, you can also open an issue in
GitHub.  To help with the debugging process, include your platform, 
command line options, and any log
files that are generated during the application execution in your
support request (as long as they contain no confidential
information).


---

[Previous Section](index.md)  \| [Next Section](configuring_user_sync_tool.md)
