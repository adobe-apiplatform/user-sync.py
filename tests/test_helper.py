import os
import re

import pytest

from user_sync.helper import JobStats, CSVAdapter


@pytest.fixture()
def field_names():
    return ['firstname', 'lastname', 'email', 'country', 'groups', 'type', 'username', 'domain']


@pytest.fixture()
def user_list():
    return [
        {'firstname': 'John', 'lastname': 'Smith', 'email': 'jsmith@example.com', 'country': 'US',
         'groups': 'AdobeCC-All', 'type': 'enterpriseID', 'username': '', 'domain': ''},
        {'firstname': 'Jane', 'lastname': 'Doe', 'email': 'jdoe@example.com', 'country': 'US', 'groups': 'AdobeCC-All',
         'type': 'federatedID', 'username': '', 'domain': ''},
        {'firstname': 'Richard', 'lastname': 'Roe', 'email': 'rroe@example.com', 'country': 'US',
         'groups': 'AdobeCC-All', 'type': '', 'username': '', 'domain': ''},
        {'firstname': '', 'lastname': 'Dorathy', 'email': '', 'country': '', 'groups': '', 'type': '',
         'username': '', 'domain': ''}
    ]


@pytest.fixture()
def adapter():
    return CSVAdapter()

@pytest.fixture()
def csv_path():
    return os.path.join('tests','fixture','helper_csv_data.csv')

def test_open_csv_file(adapter, tmpdir):
    filename = os.path.join(str(tmpdir), 'test.csv')
    open(filename, 'w').close()
    assert adapter.open_csv_file(filename, 'r')
    assert adapter.open_csv_file(filename, 'w')

    with pytest.raises(ValueError):
        adapter.open_csv_file(filename, 'invalid')


def test_guess_delimiter_from_filename(adapter):
    assert adapter.guess_delimiter_from_filename('helper_test.csv') == ','
    assert adapter.guess_delimiter_from_filename('test.tsv') == '\t'
    assert adapter.guess_delimiter_from_filename('test.mtv') == '\t'


def test_read_csv_rows(adapter, user_list, field_names, csv_path):
    csv_yield = list(adapter.read_csv_rows(csv_path, field_names))
    reduced_output = [dict(e) for e in csv_yield]
    assert reduced_output == user_list


def test_write_csv_rows(adapter, user_list, field_names, tmpdir):
    filename = os.path.join(str(tmpdir), 'test.csv')
    adapter.write_csv_rows(filename, field_names, user_list)
    csv_yield = list(adapter.read_csv_rows(filename, field_names))
    reduced_output = [dict(e) for e in csv_yield]
    assert reduced_output == user_list


def test_extra_fields(adapter, tmpdir):
    filename = os.path.join(str(tmpdir), 'test.csv')
    fields = ["field1", "field2"]

    file = open(filename, 'w')
    file.write(",".join(fields) + "\n")
    file.write("val1,val2,val3,val4")
    file.close()

    csv_yield = list(adapter.read_csv_rows(filename, fields))
    assert csv_yield == [{'field2': 'val2', 'field1': 'val1'}]


def test_log_start(log_stream):
    stream, logger = log_stream
    jobstats = JobStats('Test Job Stats')
    jobstats.log_start(logger)
    stream.flush()
    assert stream.getvalue() == '---------- Start Test Job Stats ----------------------------\n'


def test_log_end(log_stream):
    stream, logger = log_stream
    jobstats = JobStats('Test Job Stats')
    jobstats.log_end(logger)
    stream.flush()
    output = stream.getvalue()
    pattern = '(---------- End Test Job Stats \\(Total time:.*)(\\) --------\\n)'
    assert re.search(pattern, output)


def test_create_divider():
    jobstats = JobStats('Test Job Stats')
    line = jobstats.create_divider('This is a header')
    assert line == '----------This is a header----------------------------------'
