import mock
import csv
import textwrap
import StringIO
from ldap.ldapobject import LDAPObject
from aedash_connector.input import from_csv, from_ldap


def test_csv_input():
    """
    Test CSV Input

    Provide test input data via StringIO
    :return: None
    """
    test_input = StringIO.StringIO(
        textwrap.dedent("""\
        firstname	lastname	email	groups
        Test	User1	user@example.com	group1,group2\n"""))

    users = from_csv(csv.DictReader(test_input, delimiter='\t'))
    assert users.next() == {'firstname': 'Test', 'lastname': 'User1', 'disable': False,
                            'email': 'user@example.com', 'groups': ['group1', 'group2']}


def test_ldap_input():
    """
    Test LDAP Input

    Create a mock ldap query function to provide test data
    :return: None
    """

    def mock_search(*args, **kwargs):
        return [(None, {
            'givenName': ['Test'],
            'sn': ['User1'],
            'sAMAccountName': ['user'],
            'memberOf': ['CN=group1,', 'CN=group2,'],
        })]

    con = mock.create_autospec(LDAPObject)
    con.search_s = mock_search
    users = from_ldap(con, "example.com")
    assert users.next() == {'firstname': 'Test', 'lastname': 'User1', 'disable': False,
                            'email': 'user@example.com', 'groups': ['group1', 'group2']}
