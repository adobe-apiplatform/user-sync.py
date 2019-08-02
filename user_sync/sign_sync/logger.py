import logging
from time import strftime

TIME_LOGGER = strftime('%Y-%m-%d %H:%M:%S')
formatter = logging.Formatter('%(asctime)s %(module)s %(lineno)d %(levelname)s %(message)s')


class Log:

    def __init__(self):

        current_date = strftime('%m-%d-%Y')

        process_log_name = '{}_process.log'.format(current_date)
        process_log_path = 'sign_sync/logs/process/{}'.format(process_log_name)

        error_log_name = '{}_error.log'.format(current_date)
        error_log_path = 'sign_sync/logs/error/{}'.format(error_log_name)

        self.logs = dict()
        self.logs['process'] = self.setup_logger('process_log', process_log_path)
        self.logs['error'] = self.setup_logger('error_log', error_log_path)

    @staticmethod
    def setup_logger(name, log_file, level=logging.INFO):
        """
        Function setup as many loggers as you want
        :param name: str
        :param log_file: str
        :param level: str
        :return: object
        """

        handler1 = logging.FileHandler(log_file)
        handler1.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler1)

        return logger

    def get_log(self):
        """
        This method will return the logs
        :return: dict()
        """

        return self.logs
