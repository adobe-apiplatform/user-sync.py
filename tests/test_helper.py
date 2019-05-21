import os
import pytest
import user_sync.helper
from conftest import compare_list


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
    return user_sync.helper.CSVAdapter()


def test_open_csv_file(adapter):
    filename = 'blank.csv'
    open(filename, 'w').close()
    assert adapter.open_csv_file(filename, 'r')
    assert adapter.open_csv_file(filename, 'w')

    with pytest.raises(ValueError):
        adapter.open_csv_file(filename, 'invalid')
    os.remove(filename)


def test_guess_delimiter_from_filename(adapter):
    assert adapter.guess_delimiter_from_filename('helper_test.csv') == ','
    assert adapter.guess_delimiter_from_filename('test.tsv') == '\t'
    assert adapter.guess_delimiter_from_filename('test.mtv') == '\t'

def test_read_csv_rows(adapter, user_list, field_names):
    filename = 'test_read.csv'
    write_users_to_file(filename, field_names, user_list)

    csv_yield = list(adapter.read_csv_rows(filename, field_names))
    reduced_output = [dict(e) for e in csv_yield]
    assert compare_list(reduced_output, user_list)
    os.remove(filename)

def test_write_csv_rows(adapter, user_list, field_names):
    filename = 'test.csv'
    adapter.write_csv_rows(filename, field_names, user_list)
    csv_yield = list(adapter.read_csv_rows(filename, field_names))
    reduced_output = [dict(e) for e in csv_yield]
    assert compare_list(reduced_output, user_list)
    os.remove(filename)

def write_users_to_file(filename, field_names, user_list):
    file = open(filename, 'w')
    file.write(",".join(field_names) + "\n")
    for u in user_list:
        line = ""
        for c, f in enumerate(field_names):
            if f in u:
                line += u[f]
            if c < len(field_names) - 1:
                line += ","
        file.write(line + "\n")
    file.close()
