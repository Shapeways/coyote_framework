import errno
import os

__author__ = 'justin@shapeways.com'


def create_directory(directory):
    """Creates a directory if it does not exist (in a thread-safe way)

    @param directory: The directory to create
    @return: The directory specified
    """
    try:
        os.makedirs(directory)
    except OSError, e:
        if e.errno == errno.EEXIST and os.path.isdir(directory):
            pass

    return directory