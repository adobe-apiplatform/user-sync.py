import ldap
import re
import copy


_TEMPLATE = {
    "firstname": None,
    "lastname": None,
    "email": None,
    "groups": [],
    "disable": False,
}


def from_csv(reader):
    for rec in reader:
        outrec = copy.deepcopy(_TEMPLATE)
        outrec['firstname'] = rec['firstname']
        outrec['lastname'] = rec['lastname']
        outrec['email'] = rec['email']
        if not rec['groups']:
            outrec['groups'] = []
        else:
            outrec['groups'] = rec['groups'].split(',')
        yield outrec


def from_ldap(host, username, pw, domain):
    con = ldap.initialize(host)
    con.protocol_version = 3
    con.set_option(ldap.OPT_REFERRALS, 0)
    con.simple_bind_s(username, pw)

    base_dn = "dc=ccestestdomain,dc=com"
    fltr = "(objectClass=person)"
    attrs = ["givenName", "sn", "sAMAccountName", "memberOf"]
    res = con.search_s(base_dn, ldap.SCOPE_SUBTREE, fltr, attrs)

    for _, rec in res:
        if not isinstance(rec, dict):
            continue
        if 'sAMAccountName' not in rec:
            continue
        outrec = copy.deepcopy(_TEMPLATE)
        outrec['email'] = '%s@%s' % (rec['sAMAccountName'][0], domain)
        if 'givenName' in rec:
            outrec['firstname'] = rec['givenName'][0]
        if 'sn' in rec:
            outrec['lastname'] = rec['sn'][0]
        if 'memberOf' in rec:
            for g in rec['memberOf']:
                m = re.match(r"CN=(?P<group>[^,]+),", g)
                if m:
                    outrec['groups'].append(m.group('group'))
        yield outrec
