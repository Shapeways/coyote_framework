import errno
import os
import pickle

__author__ = 'justin@shapeways.com'


class TestData(object):

    def save(self, path='', filename=''):
        """Saves the data to a pkl file

        @param path: Path to save to
        @param filename: Filename
        @return: None
        """
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

        with open(os.path.join(path, filename), 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def from_file(filename):
        """Reconstructs the data object from a file

        @return: Instance of the pickled data reconstructed from file
        """
        with open(filename, 'rb') as f:
            return pickle.load(f)