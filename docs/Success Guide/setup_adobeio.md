## Setup an Adobe.io integration

- Adobe has designed a secure protocol for applications to integrate with Adobe Apis and user sync is such an application.
- Setup steps are pretty well documented:
  - For complete information about the integration setup process and certificate requirements, see  https://www.adobe.io/products/usermanagement/docs/setup
- You need to create or obtain a digital certificate to sign initial API calls.
  - The certificate is not used for SSL or any other purpose so trust chains and browser issues do not apply.
  - You can create the certificate yourself using free tools or purchase one (or obtain from your IT department).
  - You will need a public key certificate file and a private key file.
  - You’ll want to protect the private key file as you would a root password.
- Once setup, the Adobe.io console displays all needed values.  You’ll copy these into the user sync configuration file.
