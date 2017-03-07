## Identify and setup the server where user sync will run

- User sync can be run manually, but most companies will want to set up automation where user sync runs once to a few times per day automatically.
- It needs to be installed and run on a server that:
  - can access Adobe via the internet
  - Can access your directory service such as LDAP or AD
  - Is protected and secure (your administrative credentials will be stored or accessed there)
  - Stays up and is reliable
  - Has some backup and recovery capability.
  - Ideally can send email so reports can be sent by user sync to administrators
- You’ll need to work with your IT department to identify such a server and get access to it.
- Unix, OSX, or Windows are all supported by user-sync.
