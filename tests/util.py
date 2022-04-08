from collections.abc import Mapping
from copy import deepcopy
from io import StringIO

def make_dict(keylist, value):
    """
    Create a dict from a list of keys
    :param keylist: [key1, key2]
    :param value:  val
    :return: {k1:{k2:val}}
    """
    tree_dict = {}
    for i, key in enumerate(reversed(keylist)):
        val = value if i == 0 else tree_dict
        tree_dict = {
            key: val
        }
    return tree_dict

def compare_iter(a, b):
    return (len(a) == len(b) and
            {x in b for x in a} ==
            {x in b for x in a} ==
            {True})


def merge_dict(d1, d2, immutable=False):
    """
    # Combine dictionaries recursively
    # preserving the originals
    # assumes d1 and d2 dictionaries!!
    :param d1: original dictionary
    :param d2: update dictionary
    :return: modified d1
    """

    d1 = {} if d1 is None else d1
    d2 = {} if d2 is None else d2
    d1 = deepcopy(d1) if immutable else d1

    for k in d2:
        # if d1 and d2 have dict for k, then recurse
        # else assign the new value to d1[k]
        if (k in d1 and isinstance(d1[k], Mapping)
                and isinstance(d2[k], Mapping)):
            merge_dict(d1[k], d2[k])
        else:
            d1[k] = d2[k]
    return d1

# Serves as a base user for either umapi or directory user tests
def create_blank_user(
        identifier,
        firstname=None,
        lastname=None,
        groups=None,
        country="US",
        identity_type="federatedID",
        domain="example.com",
        username=None
):
    if '@' not in identifier:
        identifier = identifier + "@" + domain
    user_id = identifier.split("@")[0]
    firstname = firstname or user_id + " First"
    lastname = lastname or user_id + " Last"
    domain = domain or identifier.split("@")[-1]

    return deepcopy({
        'identity_type': identity_type,
        'type': identity_type,
        'username': username or identifier,
        'domain': domain,
        'firstname': firstname,
        'lastname': lastname,
        'email': identifier,
        'groups': groups or [],
        'member_groups': [],
        'adminRoles': [],
        'status': 'active',
        'country': country,
        'source_attributes': {
            'email': identifier,
            'identity_type': None,
            'username': user_id,
            'domain': domain,
            'givenName': firstname,
            'sn': lastname,
            'c': country}
    })



class MockResponse:

    def __init__(self, status=200, body=None, headers=None, text=None):
        self.status_code = status
        self.body = body if body is not None else {}
        self.headers = headers if headers else {}
        self.text = text if text else ""

    def json(self):
        return self.body

class ClearableStringIO(StringIO, object):

    def __init__(self):
        super(ClearableStringIO, self).__init__()

    def clear(self):
        self.truncate(0)
        self.seek(0)

    def getvalue(self, *args, **kwargs):
        self.flush()
        return super(ClearableStringIO, self).getvalue()


