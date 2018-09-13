import ldap
import uuid

class LDAPConfig:

    def __init__(self, config_loader, connector, logs):

        self.logs = logs
        self.config_loader = config_loader
        self.connector = connector

        self.ldap_config = self.load_ldap_config()
        self.address = self.ldap_config['host']
        self.base_dn = self.ldap_config['base_dn']
        self.username = self.ldap_config['username']
        self.password = self.ldap_config['password']

        # self.attributes = yml_sign_sync_config['ldap_conditions']['attributes']

        # Connection
        self.conn = None

    def load_ldap_config(self):

        directory_connector_module_name = self.config_loader.get_directory_connector_module_name()
        if directory_connector_module_name is not None:
            directory_connector_module = __import__(directory_connector_module_name, fromlist=[''])
            directory_connector = self.connector.DirectoryConnector(directory_connector_module)
            directory_connector_options = self.config_loader.get_directory_connector_options(directory_connector.name)

        return directory_connector_options

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
            self.logs.error("Invalid LDAP Credentials...")

        except ldap.SERVER_DOWN:
            self.logs.error("LDAP Server Down...")

        self.logs.info("LDAP Authenticated...")

    def disconnect(self):
        """
        This function will disconnect the application from the LDAP server
        :return:
        """

        try:
            self.conn.unbind_s()
        except Exception as e:
            self.logs.error("Failed to unbind from LDAP server...")

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
