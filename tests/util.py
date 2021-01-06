import collections


def update_dict(d, ks, u):
    k, ks = ks[0], ks[1:]
    v = d.get(k)
    if ks and isinstance(v, collections.Mapping):
        d[k] = update_dict(v, ks, u)
    else:
        d[k] = u
    return d

def compare_iter(a, b):
    return (len(a) == len(b) and
            {x in b for x in a} ==
            {x in b for x in a} ==
            {True})
