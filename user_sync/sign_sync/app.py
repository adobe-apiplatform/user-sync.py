import logging
import user_sync.sign_sync.connections.sign_connection
import user_sync.sign_sync.connections.umapi_connection

logger = logging.getLogger('sign_sync')


def run(config_loader, user_keys, config_filename=False):
    """
    This function will load up all the configuration and execute the sync function
    :param config_loader: ConfigLoader
    :param user_keys: set()
    :param config_filename: str
    :return:
    """

    # Instantiate Sign object & validate
    sign_obj = user_sync.sign_sync.connections.sign_connection.Sign(config_filename)
    sign_groups = sign_obj.get_sign_group()

    primary_config, secondary_config = config_loader.get_umapi_options()
    data_connector = user_sync.sign_sync.connections.umapi_connection.Umapi(primary_config)

    sync_users(sign_obj, sign_groups, data_connector, user_keys)


def sync_users(sign_obj, sign_groups, connector, user_keys):
    """
    This is the run function of the application.
    :param sign_obj: dict()
    :param sign_groups: list[]
    :param connector: dict()
    :param user_keys: set()
    """

    logger.info('------------------------------- Starting Sign Sync -------------------------------')

    # Get Users and Groups information from our connector
    group_list, user_list = get_data_from_connector(sign_obj, connector, user_keys)

    # Format the users and create groups that don't exist in Adobe Sign
    updated_user_list = sign_obj.get_updated_user_list(user_list)

    # Create new user groups in sign if not found
    groups_not_found_in_sign = [group for group in group_list if group not in sign_groups]
    if groups_not_found_in_sign:
        sign_obj.create_sign_group(groups_not_found_in_sign)

    # Sync users into their groups
    for user in updated_user_list:
        sign_obj.process_user(user)

    logger.info('------------------------------- Ending Sign Sync ---------------------------------')


def get_data_from_connector(sign_obj, data_connector, user_keys):
    """
    This function gets user data the main connector
    :param sign_obj: obj
    :param data_connector: dict()
    :param user_keys: set()
    :return: dict(), dict()
    """

    # Get Users and Groups information from our connector
    group_list = data_connector.query_user_groups()
    user_list = data_connector.query_users_in_groups(sign_obj.get_product_profile(), user_keys)

    return group_list, user_list
