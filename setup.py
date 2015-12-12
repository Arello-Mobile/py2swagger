# coding=utf-8

import os
from setuptools import setup

VERSION = '1.0.0'

README = """
  py2swagger

  Swagger schema builder
"""

# allow setup.py to be run from any path
os.chdir(os.path.dirname(__file__))
install_requires = [
    'PyYAML>=3.10',
    'six',
    'yapsy==1.11.223'
]

import platform

version = platform.python_version_tuple()
if version < ('2', '7'):
    install_requires.append('importlib>=1.0.1')
    install_requires.append('ordereddict>=1.1')

setup(
    name='py2swagger',
    version=VERSION,
    packages=['py2swagger'],
    package_dir={
        'py2swagger': 'src',
    },
    test_suite='src.tests',
    license='MIT',
    description='Swagger schema builder',
    long_description=README,
    install_requires=install_requires,
    extras_require={
        'reST': ['docutils>=0.8'],
    },
    author='Arello Mobile',
    url='https://github.com/Arello-Mobile/py2swagger',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points={
        'console_scripts': [
            'py2swagger = py2swagger:run',
        ]
    }
)
