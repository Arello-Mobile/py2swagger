# Swagger schema builder (``py2swagger``)

## Description

Swagger schema builder


## Install

```bash
pip install py2swagger
```

Is needed to install plugins for specific frameworks, e.g. for Django REST Framework

```bash
pip install py2swagger.ext.drf
```

## Launch

Command ``py2swagger``

```bash

usage: py2swagger [-h] [-c CONFIG] [-o OUTPUT] {some_plugin} ...

Swagger schema builder

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to custom config file
  -o OUTPUT, --output OUTPUT
                        Output file (Default stdout)
```


## Run tests

```bash
cd src/

pip install -r tests/testapp/requirements.txt

usage: python tests/run_tests.py
```
