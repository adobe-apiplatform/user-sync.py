import user_sync.sign_sync.logger
import user_sync.sign_sync.connections.sign_connection
import user_sync.sign_sync.connections.umapi_connection
import user_sync.sign_sync.thread_functions
from queue import Queue

LOGGER = user_sync.sign_sync.logger.Log()


def run(config_loader, user_keys=None):

    log_file = LOGGER.get_log()

    # Instantiate Sign object & validate
    sign_obj = user_sync.sign_sync.connections.sign_connection.Sign(log_file)
    sign_obj.validate_integration_key(sign_obj.header, sign_obj.url)
    sign_groups = sign_obj.get_sign_group()

    primary_config, secondary_config = config_loader.get_umapi_options()
    data_connector = user_sync.sign_sync.connections.umapi_connection.Umapi(primary_config)

    sync_users(log_file, sign_obj, sign_groups, data_connector, user_keys)

def sync_users(logs, sign_obj, sign_groups, connector, user_keys):
    """
    This is the run function of the application.
    :param logs: dict()
    :param sign_obj: dict()
    :param sign_groups: list[]
    :param data_connectors: dict()
    """

    logs['process'].info('------------------------------- Starting Sign Sync -------------------------------')

    # Get Users and Groups information from our connector
    group_list, user_list = get_data_from_connector(sign_obj, connector, user_keys)

    # Format the users and create groups that don't exist in Adobe Sign
    updated_user_list = sign_obj.get_updated_user_list(user_list)

    # Create new user groups in sign if not found
    groups_not_found_in_sign = [group for group in group_list if group not in sign_groups]
    if groups_not_found_in_sign:
        sign_obj.create_sign_group(group_list, LOGGER)

    # Sync users into their groups
    do_threading(updated_user_list, sign_obj.process_user)

    logs['process'].info('------------------------------- Ending Sign Sync ---------------------------------')


def get_data_from_connector(sign_obj, data_connector, user_keys):
    """
    This function gets user data the main connector
    :param sign_obj: obj
    :param data_connector: dict()
    :return: dict(), dict()
    """

    # Get Users and Groups information from our connector
    group_list = data_connector.query_user_groups()
    user_list = data_connector.query_users_in_groups(sign_obj.get_product_profile(), sign_obj.account_type, user_keys)

    return (group_list, user_list)

def do_threading(user_list, func):
    """
    This function will be start up a threading process.
    :param user_list: list[]
    :param func: FUNCTION
    :return:
    """

    queue = Queue()
    for x in range(50):
        worker = user_sync.sign_sync.thread_functions.ThreadWorker(queue, func)
        worker.start()

    for user in user_list:
        queue.put(user)

    queue.join()