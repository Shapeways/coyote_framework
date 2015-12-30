from collections import namedtuple

__author__ = 'justin@shapeways.com'


def objectify(dictionary, name='Object'):
    """Converts a dictionary into a named tuple (shallow)

    """
    o = namedtuple(name, dictionary.keys())(*dictionary.values())

    return o
