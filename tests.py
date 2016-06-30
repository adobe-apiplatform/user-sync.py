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
        firstname	lastname	email	groups	country
        Test	User1	user@example.com	group1,group2	US\n"""))

    users = from_csv(csv.DictReader(test_input, delimiter='\t'))
    assert users[0] == {'firstname': 'Test', 'lastname': 'User1', 'disable': False,
                        'email': 'user@example.com', 'groups': ['group1', 'group2'], 'country': 'US'}


def test_ldap_input():
    """
    Test LDAP Input

    Create a mock ldap query function to provide test data
    :return: None
    """

    def mock_search_s(*args, **kwargs):
        return [(None, {'distinguishedName': ['CN=group1,CN=Users,DC=example,DC=com']})]

    def mock_search_ext(*args, **kwargs):
        return 0

    def mock_result3(*args, **kwargs):
        rtype = None
        rmsgid = None
        serverctrls = []
        rdata = [(None, {
            'givenName': ['Test'],
            'sn': ['User1'],
            'sAMAccountName': ['user'],
            'memberOf': ['CN=group1,', 'CN=group2,'],
            'c': ['US'],
        })]
        return rtype, rdata, rmsgid, serverctrls

    con = mock.create_autospec(LDAPObject)
    con.search_s = mock_search_s
    con.search_ext = mock_search_ext
    con.result3 = mock_result3
    users = from_ldap(con, "example.com", ['group1'], "DC=example,DC=com", "(objectClass=user)")
    assert users[0] == {'firstname': 'Test', 'lastname': 'User1', 'disable': False,
                        'email': 'user@example.com', 'groups': ['group1', 'group2'], 'country': 'US'}
