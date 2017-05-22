---
layout: page
title: User Manual - Advanced Configuration
lang: en
nav_link: Advanced Configuration
nav_level: 2
nav_order: 60
---


## Advanced Configuration

User Sync requires additional configuration to synchronize user
data in environments with more complex data structuring.

- When you manage your Adobe ID users out of spreadsheets or your
enterprise directory, you can configure the tool not to ignore
them.
- When your enterprise includes several Adobe organizations, you
can configure the tool to add users in your organization to
groups defined in other organizations.
- When your enterprise user data includes customized attributes
and mappings, you must configure the tool to be able to recognize
those customizations.
- When you want to use username (rather than email) based logins.
- When you want to manage some user accounts manually through the Adobe Admin Console in addition to using User Sync

### Managing Users with Adobe IDs

There is a configuration option `exclude_identity_types` (in 
the `adobe_users` section of the main config file) which
is set by default to ignore Adobe ID users.  If you want User Sync to 
manage some Adobe Id type users, you must turn this option off in the 
config file by removing the `adobeID` entry from under `exclude_identity_types`.

You will probably want to set up a separate sync
job specifically for those users, possibly using CSV inputs
rather than taking inputs from your enterprise directory. If you do this, be sure
to configure this sync job to ignore Enterprise ID and Federated
ID users, or those users are likely to be removed from the
directory!

Removal of Adobe ID users via User Sync may not have the effect you desire:

* If you specify that adobeID users should be
removed from your organization, you will have to re-invite them
(and have them re-accept) if you ever want to add them back in.
* System administrators often use Adobe IDs, so removing Adobe ID
users may inadvertently remove system administrators (including
yourself)

A better practice, when managing Adobe ID users, is simply add
them and manage their group memberships, but never to remove
them.  By managing their group memberships you can disable their
entitlements without the need for a new invitation if you later
want to turn them back on.

Remember that Adobe Id accounts are owned by the end user and 
cannot be deleted.  If you apply a delete action, User Sync will 
automatically substitute the remove action for the delete action.

You can also protect specific Adobe Id users from removal by User Sync 
by using the other exclude configuration items.  See
[Protecting Specific Accounts from User Sync Deletion](#Protecting-Specific-Accounts-from-User-Sync-Deletion)
for more information.

### Accessing Users in Other Organizations

A large enterprise can include multiple Adobe organizations. For
example, suppose a company, Geometrixx, has multiple departments,
each of which has its own unique organization ID and its own
Admin Console.

If an organization uses either Enterprise or Federated user IDs,
it must claim a domain. In a smaller enterprise, the single
organization would claim the domain **geometrixx.com**. However,
a domain can be claimed by only one organization. If multiple
organizations belong to the same enterprise, some or all of them
will want to include users that belong to the enterprise domain.

In this case, the system administrator for each of these
departments would want to claim this domain for identity use. The
Adobe Admin Console prevents multiple departments from claiming
the same domain.  However, once claimed by a single department,
other departments can request access to another department's
domain. The first department to claim the domain is the *owner*
of that domain. That department is responsible for approving
any requests for access by other departments, who are then able
to access users in the domain without any special configuration
requirements.

No special configuration is required to access users in a domain
that you have been granted access to. However, if you want to add
users to user groups or product configurations that are defined
in other organizations, you must configure User Sync so that it
can access those organizations. The tool must be able to find the
credentials of the organization that defines the groups, and be
able to identify groups as belonging to an external organization.


### Accessing Groups in Other Organizations

To configure for access to groups in other organizations, you
must:

- Include additional umapi connection configuration files.
- Tell User Sync how to access these files.
- Identify the groups that are defined in another organization.

##### 1. Include additional configuration files

For each additional organization to which you require access, you
must add a configuration file that provides the access
credentials for that organization. The file has the
same format as the connector-umapi.yml file.  Each additional organization will be referred to by a short nickname (that you define).  You can name the configuration file that has the access credentials for that organization however you like.  

For example, suppose the additional organization is named "department 37".  The config file for it might be named: 

`department37-config.yml`

##### 2. Configure User Sync to access the additional files


The `adobe-users` section of the main configuration file must
include entries that reference these files, and
associate each one with the short organization name. For
example:

```YAML
adobe-users:
  connectors:
    umapi:
      - connector-umapi.yml
      - org1: org1-config.yml
      - org2: org2-config.yml
      - d37: department37-config.yml  # d37 is short name for example above
```

If unqualified file names are used, the configuration files must be in the same folder as the main configuration file that references them.

Note that, like your own connection
configuration file, they contain sensitive information that must
be protected.

##### 3. Identify groups defined externally

When you specify your group mappings, you can map an enterprise
directory group to an Adobe user group or product configuration defined in another
organization.

To do this, use the organization identifier as a prefix to the
group name. Join them with "::". For example:

```YAML
- directory_group: CCE Trustee Group
  adobe_groups:
    - "org1::Default Adobe Enterprise Support Program configuration"
    - "d37::Special Ops Group"
```

### Custom Attributes and Mappings

It is possible to define custom mappings of directory attribute
or other values to the fields used to define and update users:
first name, last name, email address, user name, country, and group membership.
Normally, standard attributes in the directory are used to
obtain these values.  You can define other attributes to be used and
specify how field values should be computed.

To do this, you must configure User Sync to recognize any non-standard
mappings between your enterprise directory user data and Adobe
user data.  Non-standard mappings include:

- Values for user name, groups, country, or email that are in or
are based on any non-standard attribute in the directory.
- Values for user name, groups, country, or email must be
computed from directory information.
- Additional user groups or products that must be added to or
removed from the list for some or all users.

Your configuration file must specify any custom attributes to be
fetched from the directory. In addition, you must specify any
custom mapping for those attributes, and any computation or
action to be taken to sync the values. The custom action is
specified using a small block of Python code. Examples and
standard blocks are provided.

The configuration for custom attributes and mappings go in a separate
configuration file.  That file is referenced from the main
configuration file in the `directory_users` section:

```
directory_users:
  extension: extenstions_config.yml  # reference to file with custom mapping information
```

Custom attribute handling is performed for each user, so the
customizations are configured in the per-user subsection of the
extensions section of the main User Sync configuration file.

```
extensions:
  - context: per_user
    extended_attributes:
      - my-attribute-1
      - my-attribute-2
    extended_adobe_groups:
      - my-adobe-group-1
      - my-adobe-group-2
    after_mapping_hook: |
        pass # custom python code goes here
```

#### Adding custom attributes

By default, User Sync captures these standard attributes for each
user from the enterprise directory system:

* `givenName` - used for Adobe-side first name in profile
* `sn` - used for Adobe-side last name in profile
* `c` - used for Adobe-side country (two-letter country code)
* `mail` - used for Adobe-side email
* `user` - used for Adobe-side username only if doing Federated ID via username

In addition, User Sync captures any attribute names that appear in
filters in the LDAP connector configuration.

You can add attributes to this set by specifying them in an
`extended_attributes` key in the main configuration file, as shown above. The
value of the `extended_attributes` key is a YAML list of strings, with
each string giving the name of a user attribute to be
captured. For example:

```YAML
extensions:
  - context: per-user
    extended_attributes:
    - bc
    - subco
```

This example directs User Sync to capture the `bc` and `subco`
attributes for every user loaded.

If one or more of the specified attributes is missing from the
directory information for a user, those attributes are
ignored. Code references to such attributes will return the
Python `None` value, which is normal and not an error.

#### Adding custom mappings

Custom mapping code is configured using an extensions section in
the main (user sync) config file. Within extensions, a per-user
section will govern custom code that's invoked once per user.

The specified code would be executed once for each user, after
attributes and group memberships have been retrieved from the
directory system, but before actions to Adobe have been
generated.

```YAML
extensions:
  - context: per-user
    extended_attributes:
      - bc
      - subco
    extended_adobe_groups:
      - Acrobat_Sunday_Special
      - Group for Test 011 TCP
    after_mapping_hook: |
      bc = source_attributes['bc']
      subco = source_attributes['subco']
      if bc is not None:
          target_attributes['country'] = bc[0:2]
          target_groups.add(bc)
      if subco is not None:
          target_groups.add(subco)
      else:
          target_groups.add('Undefined subco')
```

In this example, two custom attributes, bc, and subco, are
fetched for each user that is read from the directory. The custom
code processes the data for each user:

- The country code is taken from the first 2 characters in the bc
attribute.

    This shows how you can use custom directory attributes to provide
values for standard fields being sent to Adobe.

- The user is added to groups that come from subco attribute and
the bc attribute (in addition to any mapped groups from the group
map in the configuration file).

    This shows how to customize the group or product configuration
list to get users synced into additional groups.

If the hook code references Adobe groups or product
configurations that do not already appear in the **groups**
section of the main configuration file, they are listed under
**extended_adobe_groups**. This list effectively extends the
set of Adobe groups that are considered . See
[Advanced Group and Product Management](#advanced-group-and-product-management)
for more information.

#### Hook code variables

The code in the `after_mapping_hook` is isolated from the rest of
the User Sync program except for the following variables.

##### Input values

The following variables can be read in the custom code.  They
should not be written, and writes tot them have no effect; they
exist to express the source directory data about the user.

* `source_attributes`: A per-user dictionary of user attributes
  retrieved from the directory system. As a Python dictionary,
  technically, this value is mutable, but changing it from custom
  code has no effect.

* `source_groups`: A frozen set of directory groups found for a
specific user while traversing configured directory groups.

##### Input/output values

The following variables can be read and written by the custom
code. They come in carrying data set by the default attribute and
group mapping operations on the current directory user, and can
be written so as to change the actions performed on the
corresponding Adobe user.

* `target_attributes`: A per-user Python dictionary whose keys
are the Adobe-side attributes that are to be set. Changing a
value in this dictionary will change the value written on the
Adobe side. Because Adobe pre-defines a fixed set of attributes,
adding a key to this dictionary has no effect.  The keys in this
dictionary are:
    * `firstName` - ignored for AdobeID, used elsewhere
    * `lastName` - ignored for AdobeID, used elsewhere
    * `email` - used everywhere
    * `country` - ignored for AdobeID, used elsewhere
    * `username` - ignored for all but Federated ID
      [configured with username-based login](https://helpx.adobe.com/enterprise/help/configure-sso.html)
    * `domain` - ignored for all but Federated ID [configured with username-based login](https://helpx.adobe.com/enterprise/help/configure-sso.html)
* `target_groups`: A per-user Python set that collects the
Adobe-side user groups and product configurations to which the
user is added when `process-groups` is specified for the sync
run.  Each value is a set of names. The set is initialized by
applying the group mappings in the main configurations file, and
changes made to this set (additions or removals) will change the
set of groups that are applied to the user on the Adobe side.
* `hook_storage`: A per-user Python dictionary that is empty the
first time it is passed to custom code, and persists across
calls.  Custom code can store any private data in this
dictionary. If you use external script files, this is a suitable
place to store the code objects created by compiling these files.
* `logger`: An object of type `logging.logger` which outputs to
the console and/or file log (as per the logging configuration).

### Advanced Group and Product Management

The **group** section of the main configuration file defines a
mapping of directory groups to Adobe user groups and product
configurations.

- On the enterprise directory side, User Sync selects a set of
users from your enterprise directory, based on the LDAP query,
the `users` command line parameter, and the user filter, and
examines these users to see if they are in any of the mapped
directory groups. If they are, User Sync uses the group map to
determine which Adobe groups those users should be added to.
- On the Adobe side, User Sync examines the membership of mapped
groups and product configurations. If any user in those groups is
_not_ in the set of selected directory users, User Sync removes
that user from the group. This is usually the desired behavior
because, for example, if a user is in the Adobe Photoshop product
configuration and they are removed from the enterprise directory,
you would expect them to be removed from the group so that they
are no longer allocated a license.

![Figure 4: Group Mapping Example](media/group-mapping.png)

This workflow can present difficulties if you want to divide the
sync process into multiple runs in order to reduce the number of
directory users queried at once. For example, you could do a run
for users beginning with A-M and another with users N-Z. When you
do this, each run must target different Adobe user groups and
product configurations.  Otherwise, the run for A-M would remove
users from mapped groups who are in the N-Z set.

To configure for this case, use the Admin Console to create user
groups for each user subset (for example, **photoshop_A_M** and
**photoshop_N_Z**), and add each of the user groups separately to
the product configuration (for example, **photoshop_config**). In
your User Sync configuration, you then map only the user groups,
not the product configurations. Each sync job targets one user
group in its group map.  It updates membership in the user group,
which indirectly updates the membership in the product
configuration.

### Removing Group Mappings

There is potential confusion when removing a mapped group. Say a 
directory group `acrobat_users` is mapped to the Adobe group `Acrobat`. 
and you no longer want to map the group to `Acrobat` so you take out 
the entry. The result is that all of the users are left in the 
`Acrobat` group because `Acrobat` is no longer a mapped group so user 
sync leaves it alone. It doesn't result in removing all the users 
from `Acrobat` as you might have expected.

If you also wanted the users removed from the `Acrobat` group, you can
manually remove them using the Admin Console, or you can (at least 
temporarily) leave the entry in the group map in the configuration
file, but change the directory group to a name that you know does
not exist in the directory, such as `no_directory_group`.  The next sync 
run will notice that there are users in the Adobe group who are 
not in the directory group and 
they will all be moved.  Once this has happened, you can remove
the entire mapping from the configuration file.

### Working with Username-Based Login

On the Adobe Admin Console, you can configure a federated domain to use email-based user login names or username-based (i.e., non-email-based) login.   Username-based login can be used when email addresses are expected to change often or your organization does not allow email addresses to be used for login.  Ultimately, whether to use username-based login or email-based login depends on a company's overall identity strategy.

To configure User Sync to work with username logins, you need to set several additional configuration items.

In the `connector-ldap.yml` file:

- Set the value of `user_username_format` to a value like '{attrname}' where attrname names the directory attribute whose value is to be used for the user name.
- Set the value of `user_domain_format` to a value like '{attrname}' if the domain name comes from the named directory attribute, or to a fixed string value like 'example.com'.

When processing the directory, User Sync will fill in the username and domain values from those fields (or values).

The values given for these configuration items can be a mix of string characters and one or more attribute names enclosed in curly-braces "{}".  The fixed characters are combined with the attribute value to form the string used in processing the user.

For domains that use username-based login, the `user_username_format` configuration item should not produce an email address; the "@" character is not allowed in usernames used in username-based login.

If you are using username-based login, you must still provide a unique email address for every user, and that email address must be in a domain that the organization has claimed and owns. User Sync will not add a user to the Adobe organization without an email address.

### Protecting Specific Accounts from User Sync Deletion

If you drive account creation and removal through User Sync, and want to manually create a few accounts, you may need this feature to keep User Sync from deleting the manually created accounts.

In the `adobe_users` section of the main configuration file you can include
the following entries:

```YAML
adobe_users:
  exclude_adobe_groups: 
      - special_users       # Adobe accounts in the named group will not be removed or changed by user sync
  exclude_users:
      - ".*@example.com"    # users whose name matches the pattern will be preserved by user sync 
      - another@example.com # can have more than one pattern
  exclude_identity_types:
      - adobeID             # causes user sync to not remove accounts that are AdobeIds
      - enterpriseID
      - federatedID         # you wouldn’t have all of these since that would exclude everyone  
```

These are optional configuration items.  They identify individual or groups
of accounts and the identified accounts are protected from deletion by 
User Sync.  These accounts may still be added to or removed from user
groups or Product Configurations based on the group map entries and
the `--process-groups` command line option.  

If you want to prevent User Sync from removing these accounts from groups, only place them in groups not under control of User Sync, that is, in groups 
that are not named in the group map in the config file.

- `exclude_adobe_groups`: The values of this configuration item is a list of strings that name Adobe user groups or PCs.  Any users in any of these groups are preserved and never deleted as Adobe-only users.
- `exclude_users`: The values of this configuration item is a list of strings that are patterns that can match Adobe user names.  Any matching users are preserved and never deleted as Adobe-only users.
- `exclude_identity_types`:  The values of this configuration item is a list of strings that can be "adobeID", "enterpriseID", and "federatedID".  This causes any account that is of the listed type(s) to be preserved and never deleted as Adobe-only users.


### Working With Nested Directory Groups in Active Directory

If your directory groups are structured in a nested manner so that users are 
not in one simple named directory group, you will need to run more complex
LDAP queries to enumerate the list of users.  For example you might have a group
nesting structure like this:


    All_Divisions
		Blue_Division
		       User1@example.com
		       User2@example.com
		Green_Division
		       User3@example.com
		       User4@example.com


To handle this type of nesting structure, in your LDAP config file, 
set the value of group_filter_format as follows:

    group_filter_format: "(memberOf:1.2.840.113556.1.4.1941:=cn={group},cn=users,DC=example,DC=com)"
    
where this part of the query:

    cn={group},cn=users,DC=example,DC=com

is the full distinguished name of the group.  The entry {group} will be replaced by the actual group when User Sync runs the group membership query.  This example assumes the group is located in the 
directory in users.example.com.  If the group is located elsewhere in the directory, you
would need to provide the appropriate path to reference it.  (example.com would be replaced by
your actual domain name also.) 

Once this is set, you can use `All_Divisions` in the group map as the directory group and/or specify `--users group All_Divisions` as the source for users.

How this works is explained in the accepted answer to this [StackOverflow](http://stackoverflow.com/questions/6195812/ldap-nested-group-membership) question and in this [MS technote](https://msdn.microsoft.com/en-us/library/aa746475%28VS.85%29.aspx). AD supports the LDAP_MATCHING_RULE_IN_CHAIN predicate which will search the entire ancestry tree to find containment.  1.2.840.113556.1.4.1941 is the precise OID you must specify to use that predicate.

This can be a very expensive filter, and should be used very carefully.

---
