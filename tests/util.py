import collections
from copy import deepcopy


def update_dict(d, ks, u):
    k, ks = ks[0], ks[1:]
    v = d.get(k)
    if ks and isinstance(v, collections.Mapping):
        d[k] = update_dict(v, ks, u)
    else:
        d[k] = u
    return d

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
        if (k in d1 and isinstance(d1[k], collections.Mapping)
                and isinstance(d2[k], collections.Mapping)):
            merge_dict(d1[k], d2[k])
        else:
            d1[k] = d2[k]
    return d1

def compare_iter(a, b):
    return (len(a) == len(b) and
            {x in b for x in a} ==
            {x in b for x in a} ==
            {True})