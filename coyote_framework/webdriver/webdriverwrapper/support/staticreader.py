"""
Module to read static files; static directory must be in same directory as this module
"""

__author__ = 'justin'

import os


def get_static_directory():
    """Retrieves the full path of the static directory

    @return: Full path of the static directory
    """
    directory = templates_dir = os.path.join(os.path.dirname(__file__), 'static')
    return directory


def read_css_file(filename):
    """Reads the contents of a css file in the css directory

    @return: Contents of the specified file
    """
    with open(os.path.join(get_static_directory(), 'css/{filename}'.format(filename=filename))) as f:
        contents = f.read()
    return contents


def read_html_file(filename):
    """Reads the contents of an html file in the css directory

    @return: Contents of the specified file
    """
    with open(os.path.join(get_static_directory(), 'html/{filename}'.format(filename=filename))) as f:
        contents = f.read()
    return contents