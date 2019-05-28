import os
import six
import pytest
import logging
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


#### These will be removed
def compare_dictionary(actual, expected):
    if len(actual) != len(expected):
        return False
    for key in actual:
        if key not in expected:
            return False
        elif isinstance(actual[key], dict):
            if not compare_dictionary(actual[key], expected[key]):
                return False
        elif isinstance(actual[key], list):
            if not compare_list(actual[key], expected[key]):
                return False
        else:
            if not actual[key]: actual[key] = None
            if not expected[key]: expected[key] = None
            if six.text_type(actual[key]) != six.text_type(expected[key]):
                return False
    return True


def compare_list(actual, expected):
    if len(actual) != len(expected):
        return False
    for act in actual:
        matched = False
        for exp in expected:
            if type(act) == type(exp):
                if isinstance(act, dict):
                    check = compare_dictionary(act, exp)
                elif isinstance(act, list):
                    check = compare_list(act, exp)
                else:
                    check = six.text_type(act) == six.text_type(exp)
                matched = True if check else matched
        if matched == False:
            return False

    return True
