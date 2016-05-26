_TEMPLATE = {
    "firstname": None,
    "lastname": None,
    "email": None,
    "groups": [],
    "disable": False,
}


def from_csv(reader):
    for rec in reader:
        outrec = _TEMPLATE
        outrec['firstname'] = rec['firstname']
        outrec['lastname'] = rec['lastname']
        outrec['email'] = rec['email']
        if not rec['groups']:
            outrec['groups'] = []
        else:
            outrec['groups'] = rec['groups'].split(',')
        if rec['disable'] == 'Y':
            outrec['disable'] = True
        else:
            outrec['disable'] = False
        yield outrec
