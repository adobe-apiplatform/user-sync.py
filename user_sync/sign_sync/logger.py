import logging
from time import strftime

TIME_LOGGER = strftime('%Y-%m-%d %H:%M:%S')
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s')


class Log:

    def __init__(self, path=None):
        self.logs = dict()

        if path is not None:
            self.logs['api'] = self.setup_logger('api_log', '{}/sign_sync/logs/api.log'.format(path))
            self.logs['process'] = self.setup_logger('process_log', '{}/sign_sync/logs/process.log'.format(path))
            self.logs['error'] = self.setup_logger('error_log', '{}/sign_sync/logs/error.log'.format(path))
        else:
            self.logs['api'] = self.setup_logger('api_log', 'sign_sync/logs/api.log')
            self.logs['process'] = self.setup_logger('process_log', 'sign_sync/logs/process.log')
            self.logs['error'] = self.setup_logger('error_log', 'sign_sync/logs/error.log')

    @staticmethod
    def setup_logger(name, log_file, level=logging.INFO):
        """
        Function setup as many log handlers
        :param name: str
        :param log_file: str
        :param level: str
        :return: object
        """

        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

    def get_logs(self):
        """
        This method will return the logs
        :return: dict()
        """

        return self.logs

    @staticmethod
    def log_error_code(logs, res):
        """
        This method will log errors
        :param logs: dict()
        :param res: str
        :return:
        """

        logs['error'].error(res.status_code)
        logs['error'].error(res.headers)
        logs['error'].error(res.text)
        exit(res.status_code)