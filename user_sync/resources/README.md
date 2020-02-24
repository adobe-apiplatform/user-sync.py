### User Sync Tool

The User Sync Tool is written in Python, but is available as a self-contained executable. In this format, the User Sync Tool is able to run without an external Python interpreter (no need to install python). This enhances both the security and convenience of using the tool. The tool is alternatively available as a PEX format artifact that can be run from a Python environment.

All versions are available on Windows, CentOS, and Ubuntu. See the releases page for details.

### UST without Extension Config.

The extension is a features that allows a user to use pure Python code to drive sync logic. To further improve security, the tool is available without the extension option. This version of the User Sync Tool removes this feature and prevents injection of malicious code.

