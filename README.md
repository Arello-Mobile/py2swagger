# Python OpenAPI Specification generator

Tool for automated or semi-automated generate a [OpenAPI Specification](https://github.com/OAI/OpenAPI-Specification)
(aka Swagger Specification) for Web APIs written with Python and famous frameworks, such as:
- [Django REST Framework](https://github.com/tomchristie/django-rest-framework) (DRF>=2; Django>=1.6)
- [Falcon](https://github.com/falconry/falcon) (falcon>=0.3)
- flask
- bottle
- and ever you own framework

Supported only v2 OpenAPI Specification


## Why?

This tool is written as part of our Documentation Toolkit which we use in our job daily.
The main idea of toolkit is to make a process of creating and updating documentation able to be automated

Other parts of our toolkit is:

- [py2swagger](https://github.com/Arello-Mobile/py2swagger)
- [swagger2rst](https://github.com/Arello-Mobile/swagger2rst)
- [sphinx-confluence](https://github.com/Arello-Mobile/sphinx-confluence)
- [confluence-publisher](https://github.com/Arello-Mobile/confluence-publisher)


# Install

Install from [PyPI](https://pypi.python.org/pypi/py2swagger) with

```
$ pip install py2swagger
```


## Usage

```
usage: py2swagger [-h] [-c CONFIG] [-r ROOT] [-o OUTPUT]
                  {falcon,drf,simple} ...

Swagger schema builder

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config file
  -r ROOT, --root ROOT  Path to project root. Default is current directory or
                        configuration file location
  -o OUTPUT, --output OUTPUT
                        Output file (Default stdout)

plugins:
  {falcon,drf,simple}
    falcon
    drf
    simple              Plugin for all applications
```


## Run tests

```bash
python setup.py test
```
