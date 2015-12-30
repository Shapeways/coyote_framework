"""

"""

import random
import os
import re

# Read the words from the nouns.text
word_file_directory = os.path.dirname(os.path.realpath(__file__))
word_file_path = os.path.join(word_file_directory, 'nouns.txt')

with open(word_file_path, 'r') as f:
    contents = f.read()
words = re.split("\s+", contents)

def random_word():
    """

    @return:
    """
    return random.choice(words)


def random_words_string(count=1, maxchars=None, sep=''):
    """Gets a
    """
    nouns = sep.join([random_word() for x in xrange(0, count)])

    if maxchars is not None and nouns > maxchars:
        nouns = nouns[0:maxchars-1]

    return nouns