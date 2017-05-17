#!/usr/bin/env python
__author__ = 'matt'

from setuptools import setup, find_packages

setup(
    name='coyote-framework',
    version='0.1.5',
    author='Shapeways',
    author_email='api@shapeways.com',
    packages=find_packages(),
    package_data={'coyote_framework': ['config/**/*.cfg']},
    url = 'https://github.com/Shapeways/coyote_framework',
    download_url = 'https://github.com/Shapeways/coyote_framework/archive/0.1.5.tar.gz',
    description='Python-based testing framework'
)
