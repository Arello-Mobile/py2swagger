import os
from setuptools import setup, find_packages


setup(
    name='py2swagger',
    version='1.0.0',
    packages=find_packages(exclude=('tests', 'tests.*')),
    license='MIT',
    description='Swagger schema builder',
    long_description=open('README.rst' if os.path.exists('README.rst') else 'README.md').read(),
    install_requires=open('requirements.txt').read(),
    extras_require={
        'reST': ['docutils>=0.8'],
    },
    tests_require=['nose'],
    test_suite='nose.collector',
    author='Arello Mobile',
    url='https://github.com/Arello-Mobile/py2swagger',
    platforms='Posix; MacOS X; Windows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Documentation',
    ],
    entry_points={
        'console_scripts': [
            'py2swagger = py2swagger:run',
        ]
    },
    package_data={'py2swagger.plugins': ['*.py2swagger']}
)
