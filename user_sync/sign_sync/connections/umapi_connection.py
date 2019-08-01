import umapi_client

class Umapi:

    def __init__(self, config):

        # Create a connection with UMAPI
        self.conn = umapi_client.Connection(ims_host=config["server"]['ims_host'],
                                            org_id=config["enterprise"]["org_id"],
                                            user_management_endpoint="https://{}/v2/usermanagement".format(
                                                config['server']['host']),
                                            auth_dict=config["enterprise"])

    def query_users_in_groups(self, product_profile, account_type, user_keys):
        """
        This function makes a query for users in a given list of groups.
        :param groups: list[]
        :param account_type: str
        :return: dict()
        """

        connector_user_info_list = []

        res = umapi_client.UsersQuery(self.conn, in_group=product_profile[0], direct_only=False)
        umapi_user_list = res.all_results()

        for key in user_keys:
            key_info = key.split(',')
            user_email = key_info[1]
            if any(user['email'] == user_email and connector_user_info_list.append(user) for user in umapi_user_list):
                pass

        return connector_user_info_list

    def query_user_groups(self):
        """
        This function will query UMAPI for group names.
        :return: list[]
        """

        group_list = list()
        user_groups = umapi_client.UserGroupsQuery(self.conn)

        for user_group in user_groups:
            group_list.append(user_group['groupName'])

        return group_list
