---
layout: default
lang: en
nav_link: Setup Server
nav_level: 2
nav_order: 260
---

# Identify and Setup the Server Where User Sync Will Run

[Previous Section](setup_adobeio.md) \| [Back to Contents](index.md) \|  [Next Section](install_sync.md)


User Sync can be run manually, but most companies will want to set up automation where User Sync runs once to a few times per day automatically.

It needs to be installed and run on a server that:

  - Can access Adobe via the internet
  - Can access your directory service such as LDAP or AD
  - Is protected and secure (your administrative credentials will be stored or accessed there)
  - Stays up and is reliable
  - Has some backup and recovery capability.
  - Ideally can send email so reports can be sent by User Sync to administrators

You’ll need to work with your IT department to identify such a server and get access to it.
Unix, OSX, or Windows are all supported by User Sync.

&#9744; Get a server allocated for the purpose of running User Sync.  Note that you can do initial setup and experiments using User Sync on some other machine such as your laptop or desktop machine as long as it meets the criteria above.

&#9744; Get a login to that machine that has sufficient capability to install and run sync.  This can usually be a non-privileged account.




[Previous Section](setup_adobeio.md) \| [Back to Contents](index.md) \|  [Next Section](install_sync.md)

