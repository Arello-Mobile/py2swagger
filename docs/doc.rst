Swagger schema builder (``py2swagger``)
=======================================

Description
~~~~~~~~~~~

Swagger schema builder


Install
~~~~~~~

.. code-block:: bash

    pip install py2swagger


Is needed to install plugins for specific frameworks, e.g. for Django REST Framework

.. code-block:: bash

    pip install py2swagger.ext.drf


Launch
~~~~~~

Command ``py2swagger``

.. code-block:: bash

    usage: py2swagger [-h] [-c CONFIG] [-o OUTPUT] {some_plugin} ...

    Swagger schema builder

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            Path to custom config file
      -o OUTPUT, --output OUTPUT
                            Output file (Default stdout)

Config
~~~~~~


Example

.. code-block:: python

    REST_INSPECTOR_SETTINGS = {
        'api_base_url': 'api/'
    }

    SWAGGER_SETTINGS = {
        'title': 'API title',
        'description': 'Description'
        'version': '0.0.1',
        'basePath': '/',
        'host': '',
        'api_key': '',
        'token_type': 'Token',
        'consumes': [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data',
        ],
        'produce': [
            'application/json',
        ],
        'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    }

``api_base_url``
----------------

Start path for all API endpoints.
All endpoints, what paths not start with ``api_base_url`` will ignore


``SWAGGER_SETTINGS``
--------------------

Swagger parameters for output file


Plugins
-------

`Yapsy`_ is base of plugin system. Every plugin should be single package.

``py2swagger`` provides plugin interface through class ``Py2SwaggerPlugin``.

.. _Yapsy: http://yapsy.sourceforge.net/


Public interface
~~~~~~~~~~~~~~~~

 - ``help`` - field for plugin description
 - ``set_parser_arguments(parser)`` - method for set additional arguments to command-line interface
 - ``run(arguments, *args, **kwargs)`` - method for launching plugin logic

Plugin registration
~~~~~~~~~~~~~~~~~~~

Do registration through `Plugin Info File Format`_ with ``.py2swagger`` extension.
File must located in folder ``site-packages`` of your virtualenv.
Keyword Module should be set by name of plugin package.

.. _Plugin Info File Format: http://yapsy.sourceforge.net/PluginManager.html#plugin-info-file-format
