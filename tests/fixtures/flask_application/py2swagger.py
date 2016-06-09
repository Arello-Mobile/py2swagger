from flask_app import hello_world


SWAGGER_SETTINGS = {
    'title': 'Flask Test Application API',
    'version': '1.0.0',
    'basePath': '/',
    'host': '',
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

PLUGIN_SETTINGS = {
    'endpoints': [
        ('/hello', 'GET', hello_world),
    ]
}
