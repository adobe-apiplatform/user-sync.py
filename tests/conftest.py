import logging
import os
import pytest
from six import StringIO
from user_sync import config


@pytest.fixture
def fixture_dir():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), 'fixture'))


@pytest.fixture
def cli_args():
    def _cli_args(args_in):
        """
        :param dict args:
        :return dict:
        """

        args_out = {}
        for k in config.ConfigLoader.invocation_defaults:
            args_out[k] = None
        for k, v in args_in.items():
            args_out[k] = v
        return args_out

    return _cli_args


@pytest.fixture
def log_stream():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    yield stream, logger
    handler.close()
