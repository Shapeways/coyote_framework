#!/usr/bin/env python
__author__ = 'matt'

from setuptools import setup

setup(
    name='coyote-framework',
    version='0.1.4',
    author='Shapeways',
    author_email='api@shapeways.com',
    packages=['coyote_framework'],
    package_data={'coyote_framework': ['config/**/*.cfg']},
    url = 'https://github.com/Shapeways/coyote_framework',
    download_url = 'https://github.com/Shapeways/coyote_framework/archive/0.1.2.tar.gz',
    description='Python-based testing framework'
)
