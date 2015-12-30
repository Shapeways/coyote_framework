#!/usr/bin/env python
__author__ = 'matt'

from setuptools import setup, find_packages

setup(
    name='coyote-framework',
    version='0.1.0',
    author='Shapeways',
    author_email='api@shapeways.com',
    install_requires=[
        'BeautifulSoup',
        'EasyProcess==0.1.6',
        'MySQL-python==1.2.5',
        'Pillow==2.3.0',
        'PyVirtualDisplay==0.1.3',
        'argparse==1.2.1',
        'beautifulsoup4==4.3.2',
        'bitstring==3.1.3',
    ],
    packages=find_packages(),
    description='Python-based testing framework',
)
