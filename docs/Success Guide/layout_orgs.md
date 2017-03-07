## Layout Your Organization, Groups, and Directories

### Simplest Case
You’ll need the LDAP query that selects the set of users to be sync’d with Adobe

Most configurations look like this.

![Simple Configuration](images/layout_orgs_simple.PNG)

### Multiple Adobe Organizations

You’ll need two LDAP queries that select the sets of users to be sync’d with Adobe

You’ll also need to run two sync configurations; one for each organization

If licenses in one org are to be used by users in the other org, setup is more complex

![Multi Configuration](images/layout_orgs_multi.png)

### Multi-Directory and Multi-org case
This is basically two instances of everything; You’ll need to run two sync configurations; one for each directory and organization

If licenses in one org are to be used by users in the other org, setup is more complex

![Multi orgs and multiple directories](images/layout_orgs_multi_dir_multi_org.png)

### Multi-Directory and single org case
You’ll need to run two sync configurations; one for each directory

User Groups (UG) and Product License Configurations (PLC) must not overlap

You cannot have user sync delete users when configured this way.

![Multi directories and single org](images/layout_orgs_multi_dir_single_org.png)
