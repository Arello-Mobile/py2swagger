SWAGGER_SETTINGS = {
    'title': 'Bottle Test Application API',
    'version': '1.0.0',
    'basePath': '/',
    'host': 'localhost',
    'consumes': [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data',
    ],
    'produce': [
        'application/json',
    ],
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'securityDefinitions': {
        'basic': {'type': 'basic'}
    }
}

PLUGIN_SETTINGS = {
    'endpoints': [
        ('/world', 'get', 'bottle_app.world'),
        ('/hello', 'get', 'bottle_app.hello'),
    ]
}
