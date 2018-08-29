import ldap
import uuid
import yaml

class LDAPConfig:

    def __init__(self, logs):

        self.logs = logs

        yml_ldap_config = yaml.load(open('connector-ldap.yml'))
        yml_sign_sync_config = yaml.load(open('sign_sync/connector-sign-sync.yml'))

        self.address = yml_ldap_config['host']
        self.base_dn = yml_ldap_config['base_dn']
        self.username = yml_ldap_config['username']
        self.password = yml_ldap_config['password']

        self.attributes = yml_sign_sync_config['ldap_conditions']['attributes']
        self.attributes = self.attributes.split(", ")

        # Connection
        self.conn = None

    def authenticate(self):
        """
        This function will authenticate a connection with the LDAP server.
        :return:
        """

        # set options for LDAP connection
        self.conn = ldap.initialize('{}'.format(self.address))
        self.conn.protocol_version = 3
        self.conn.set_option(ldap.OPT_REFERRALS, 0)

        # attempt to connect to the LDAP server
        try:
            self.conn.simple_bind_s(self.username, self.password)

        except ldap.INVALID_CREDENTIALS:
            self.logs['error'].error("Invalid LDAP Credentials...")

        except ldap.SERVER_DOWN:
            self.logs['error'].error("LDAP Server Down...")

        self.logs['process'].info("LDAP Authenticated...")

    def disconnect(self):
        """
        This function will disconnect the application from the LDAP server
        :return:
        """

        try:
            self.conn.unbind_s()
        except Exception as e:
            self.logs['error'].error("Failed to unbind from LDAP server...")

    @staticmethod
    def decode_ldap_guid(code):
        """
        This function decode the GUID for ldap users
        :param code:
        :return:
        """

        guid = code
        guid = uuid.UUID(bytes=guid)

        return guid


    def get_extra_ldap_attribute(self, user_name):

        base_dn = "CN=Users, DC=test, DC=local"
        base_dn_result = self.conn.search_s(base_dn, ldap.SCOPE_SUBTREE, "(CN={})".format(user_name))
        user_data = base_dn_result[0][1]

        temp_user_info = dict()

        if 'company' in user_data:
            temp_user_info['company'] = user_data['company'][0].decode("utf-8")
        if 'title' in user_data:
            temp_user_info['title'] = user_data['title'][0].decode("utf-8")

        return temp_user_info
