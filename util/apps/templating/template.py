__author__ = 'justin'

import re

TAG_OPEN = '{'
TAG_CLOSE = '}'


def parse_tags_from_string(string):
    pattern = '(' + TAG_OPEN + '.*?' + TAG_CLOSE + ')'
    matches = re.findall(pattern, string)
    return matches


def build_string_from_collection(template, collection):
    string = template
    tags = parse_tags_from_string(template)

    if isinstance(collection, (list, tuple)):
        for tag in tags:
            tag_inner = tag.replace(TAG_OPEN, '').replace(TAG_CLOSE, '')

            # accept only integral indeces for collections of type list and tuple
            if tag_inner.isdigit() and '.' not in tag_inner and '-' not in tag_inner:
                index = int(tag_inner)
                try:
                    string = string.replace(tag, str(collection[index]))
                except IndexError:
                    pass

    elif isinstance(collection, dict):
        for tag in tags:
            tag_inner = tag.replace(TAG_OPEN, '').replace(TAG_CLOSE, '')
            key = tag_inner
            try:
                string = string.replace(tag, str(collection[key]))
            except KeyError:    # ignore if dictionary doesn't have the key
                pass

    return string


def build_string_from_method_args(template, args=(), kwargs={}):
    string = template
    string = build_string_from_collection(string, args)
    string = build_string_from_collection(string, kwargs)
    return string
