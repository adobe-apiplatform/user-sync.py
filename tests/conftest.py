import os
import pytest


@pytest.fixture
def fixture_dir():
    return os.path.abspath(
           os.path.join(
             os.path.dirname(__file__), 'fixture'))
