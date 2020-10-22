#!/usr/bin/env python3
import uuid
from setuptools import setup, find_packages
import pathlib
import pkg_resources

with pathlib.Path('requirements.txt').open() as requirements_txt:
    reqs = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name='Meerkat Analysis',
    version='0.0.1',
    long_description=__doc__,
    packages=find_packages(),
    package_data={'meerkat_analysis': ['style/*']},
    install_requires=reqs,
    test_suite='meerkat_analysis.test'
)
