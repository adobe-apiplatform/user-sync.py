import textwrap
import yaml


def example_config():
    return textwrap.dedent("""
        server:
          host: usermanagement.adobe.io
          endpoint: /v2/usermanagement
          ims_host: ims-na1.adobelogin.om
          ims_endpoint_jwt: /ims/exchange/jwt

        enterprise:
          domain: example.com
          org_id: [ORG ID]
          api_key: [API KEY]
          client_secret: [CLIENT SECRET]
          tech_acct: [TECH ACCT ID]
          priv_key_path: private.key""")


init = yaml.load
group_config = yaml.load_all
