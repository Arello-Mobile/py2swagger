# coding=utf-8

import os
import platform
from setuptools import setup

VERSION = '1.0.0'

README = """
  py2swagger

  Swagger schema builder
"""

# allow setup.py to be run from any path
os.chdir(os.path.abspath(os.path.dirname(__file__)))
install_requires = [
    'PyYAML>=3.10',
    'six',
    'yapsy==1.11.223'
]

setup(
    name='py2swagger',
    version=VERSION,
    packages=['py2swagger'],

    license='MIT',
    description='Swagger schema builder',
    long_description=README,
    install_requires=install_requires,
    extras_require={
        'reST': ['docutils>=0.8'],
    },
    tests_require=[
        'nose',
    ],
    test_suite='nose.collector',
    author='Arello Mobile',
    url='https://github.com/Arello-Mobile/py2swagger',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points={
        'console_scripts': [
            'py2swagger = py2swagger:run',
        ]
    }
)
