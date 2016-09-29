import ldap
import re
import copy
import logging
from ldap.controls import SimplePagedResultsControl


_TEMPLATE = {
    "firstname": None,
    "lastname": None,
    "email": None,
    "groups": [],
    "disable": False,
    "country": "",
}


def from_csv(reader):
    """
    Get Directory users from CSV file

    :param reader: CSV DictReader object
    :return: Generator yields one user record per iteration
    """
    users = []
    for rec in reader:
        outrec = copy.deepcopy(_TEMPLATE)
        outrec['firstname'] = rec['firstname']
        outrec['lastname'] = rec['lastname']
        outrec['email'] = rec['email']
        outrec['country'] = rec['country']
        if not rec['groups']:
            outrec['groups'] = []
        else:
            outrec['groups'] = rec['groups'].split(',')
        users.append(outrec)
    return users


def from_ldap(con, domain, groups, base_dn, fltr, email_id=None):
    """
    Get directory users from LDAP query

    :param con: LDAP con object
    :param domain: Enterprise Domain
    :return: Generator yields one user record per iteration
    """

    users = {}
    for group in groups:
        logging.info("Getting DN for group '%s'", group)
        res = con.search_s(
            base_dn,
            ldap.SCOPE_SUBTREE,
            filterstr="(&(objectCategory=group)(cn=%s))" % group,
            attrlist=['distinguishedName']
        )

        groupdn = [o['distinguishedName'][0] for _, o in res if 'distinguishedName' in o]
        if groupdn:
            groupdn = groupdn[0]
        else:
            continue

        logging.info("DN: %s", groupdn)

        qfltr = fltr % {'groupdn': groupdn}

        attrs = ["givenName", "sn", "sAMAccountName", "memberOf", "c"]
        if email_id:
            attrs.append(email_id)
        page_size = 100

        lc = SimplePagedResultsControl(True, size=page_size, cookie='')

        pages = 0
        while True:
            msgid = con.search_ext(
                base_dn,
                ldap.SCOPE_SUBTREE,
                filterstr=qfltr,
                attrlist=attrs,
                serverctrls=[lc]
            )
            pages += 1
            logging.info("Request LDAP users page %d" % pages)
            rtype, rdata, rmsgid, serverctrls = con.result3(msgid)
            for _, rec in rdata:
                outrec = copy.deepcopy(_TEMPLATE)
                if not isinstance(rec, dict):
                    continue
                if email_id:
                    outrec['email'] = rec[email_id][0]
                else:
                    if 'sAMAccountName' not in rec:
                        continue
                    outrec['email'] = '%s@%s' % (rec['sAMAccountName'][0], domain)
                if 'givenName' in rec:
                    outrec['firstname'] = rec['givenName'][0]
                if 'sn' in rec:
                    outrec['lastname'] = rec['sn'][0]
                if 'c' in rec:
                    outrec['country'] = rec['c'][0]
                if 'memberOf' in rec:
                    for g in rec['memberOf']:
                        m = re.match(r"CN=(?P<group>[^,]+),", g)
                        if m:
                            outrec['groups'].append(m.group('group'))
                if outrec['email'] not in users:
                    users[outrec['email']] = outrec

            pctrls = [c for c in serverctrls
                      if c.controlType == SimplePagedResultsControl.controlType]
            if not pctrls:
                print logging.warn('Warning: Server ignores RFC 2696 control.')
                break

            cookie = pctrls[0].cookie
            lc.cookie = cookie
            if not cookie:
                break

    return users.values()


def make_ldap_con(host, username, pw, require_tls_cert=True):
    """
    Make an LDAP con object

    :param host: LDAP Host
    :param username: LDAP User
    :param pw: LDAP Domain
    :param require_tls_cert: If False, do not force cert validation [DEFAULT: True]
    :return: LDAP con object
    """

    if not require_tls_cert:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    con = ldap.initialize(host)
    #con.start_tls_s()
    con.protocol_version = ldap.VERSION3
    con.set_option(ldap.OPT_REFERRALS, 0)
    con.simple_bind_s(username, pw)
    return con
