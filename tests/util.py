import collections


def update_dict(d, ks, u):
    k, ks = ks[0], ks[1:]
    v = d.get(k)
    if isinstance(v, collections.Mapping):
        d[k] = update_dict(v, ks, u)
    else:
        d[k] = u
    return d
