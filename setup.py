#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='avio',
    version='0.1.1',
    description='',
    packages=find_packages(),
    install_requires=required,
)
