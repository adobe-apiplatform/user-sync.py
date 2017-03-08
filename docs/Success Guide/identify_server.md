## Identify and setup the server where user sync will run

[Previous Section](setup_adobeio.md) | [Back to Contents](Contents.md) |  [Next Section](install_sync.md)


User sync can be run manually, but most companies will want to set up automation where user sync runs once to a few times per day automatically.

It needs to be installed and run on a server that:

  - can access Adobe via the internet
  - Can access your directory service such as LDAP or AD
  - Is protected and secure (your administrative credentials will be stored or accessed there)
  - Stays up and is reliable
  - Has some backup and recovery capability.
  - Ideally can send email so reports can be sent by user sync to administrators

You’ll need to work with your IT department to identify such a server and get access to it.
Unix, OSX, or Windows are all supported by user-sync.

&#9744; Get a server allocated for the purpose of running user sync.  Note that you can do initial setup and experiments using user sync on some other machine such as your laptop or desktop machine as long as it meets the criteria above.

&#9744; Get a login to that machine that has sufficient capability to install and run sync.  This can usually be a non-privileged account.




[Previous Section](setup_adobeio.md) | [Back to Contents](Contents.md) |  [Next Section](install_sync.md)

