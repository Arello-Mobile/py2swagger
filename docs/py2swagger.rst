Config
~~~~~~


Example

.. code-block:: python

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


Default Plugin
--------------

Nested in ``py2swagger``. This plugin usage ``API Map`` to collect "paths", "definitions" and "securityDefinitions".

``API Map``
~~~~~~~~~~~

Python list of tuples: (path, method, callback)

.. code-block:: python
    MAP = [
        ('/api/list', 'get', 'app.views.list_callback'),
        ('/api/create', 'post', 'app.views.create_callback'),
    ]


Parameters
~~~~~~~~~~

  - map - path to ``API Map``



Usage Example:
.. code-block:: bash

    py2swagger -c config.py default_plugin path.to.MAP

