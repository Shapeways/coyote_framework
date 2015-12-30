__author__ = 'justin'


def encode_collection(collection, encoding='utf-8'):
    """Encodes all the string keys and values in a collection with specified encoding"""

    if isinstance(collection, dict):
        return dict((encode_collection(key), encode_collection(value)) for key, value in collection.iteritems())
    elif isinstance(collection, list):
        return [encode_collection(element) for element in input]
    elif isinstance(collection, unicode):
        return collection.encode(encoding)
    else:
        return collection


def get_delimited_string_from_list(_list, delimiter=', ', wrap_values_with_char=None, wrap_strings_with_char=None):
    """Given a list, returns a string representation of that list with specified delimiter and optional string chars

    _list -- the list or tuple to stringify
    delimiter -- the the character to seperate all values
    wrap_values_with_char -- if specified, will wrap all values in list with this character in the representation
    wrap_strings_with_char -- if specified, will wrap only values of type str with this character in the representation
    """

    if wrap_values_with_char is not None:
        return delimiter.join('{wrapper}{val}{wrapper}'.format(
            val=v,
            wrapper=wrap_values_with_char
        ) for v in _list)
    elif wrap_strings_with_char is not None:
        return delimiter.join(str(v) if not isinstance(v, str) else '{wrapper}{val}{wrapper}'.format(
            val=v,
            wrapper=wrap_strings_with_char
        ) for v in _list)
    else:
        return delimiter.join(str(v) for v in _list)