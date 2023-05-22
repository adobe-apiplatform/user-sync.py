# Features

* 8c4ea5c Implement unconditional username update

# Fixes

* #811 Fix user email update failures

# Build Changes

* Github Actions no longer maintains a build for Ubuntu Bionic (18.04),
  so automated `bionic` builds are no longer available. Automated builds
  for 22.04 Jammy have been added with the `jammy` label.

# Advisory

This is a pre-release and may not be stable for production use. The username
update feature is under development and will currently update the username of
any user that can be identified as being in need of a username update. This
may have unexpected side effects.
