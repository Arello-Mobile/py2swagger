import os
import sys
import argparse
from importlib import import_module

from falcon.testing import TestBase

from py2swagger.plugins import Py2SwaggerPluginException
from py2swagger.plugins.falcon import FalconMethodIntrospector, FalconPy2SwaggerPlugin

from .. import unordered, FIXTURES_PATH


class FalconIntrospectorTestCase(TestBase):

    def setUp(self):
        sys.path.append(os.path.join(FIXTURES_PATH, 'falcon_application'))
        self.app = import_module('falcon_app').app
        self.generated_routes = FalconPy2SwaggerPlugin().generate_routes(self.app._router._roots)
        self.filtered_methods = ('method_not_allowed', 'on_options')

    def tearDown(self):
        sys.path.remove(os.path.join(FIXTURES_PATH, 'falcon_application'))

    def test_get_operation(self):
        expected_operation = {
            'tags': ['test'],
            'summary': 'Handles GET requests for another test',
            'security': ['api_key'],
            'responses': {
                '200': {'schema': {'type': 'string'}}
            }
        }
        path, method_map = next(self.generated_routes)
        for method in method_map:
            f = method_map[method]
            if hasattr(f, '__self__') and f.__name__ not in self.filtered_methods:
                operation = FalconMethodIntrospector(f).get_operation()
                self.assertDictEqual(expected_operation, unordered(operation))

    def test_get_security_definitions(self):
        expected_result = {
            'api_key': {
                'type': 'apiKey',
                'in': 'Header',
                'name': 'Authorization'
            }
        }

        path, method_map = next(self.generated_routes)
        for method in method_map:
            f = method_map[method]
            if hasattr(f, '__self__') and f.__name__ not in self.filtered_methods:
                security_definitions = FalconMethodIntrospector(f).get_security_definitions()
                self.assertEqual(expected_result, unordered(security_definitions))


class FalconPy2SwaggerPluginTestCase(TestBase):

    def setUp(self):
        sys.path.append(os.path.join(FIXTURES_PATH, 'falcon_application'))
        self.app = import_module('falcon_app').app
        self.filtered_methods = ('method_not_allowed', 'on_options')

    def tearDown(self):
        sys.path.remove(os.path.join(FIXTURES_PATH, 'falcon_application'))

    def test_run(self):
        expected_result = {
            'paths': {
                '/test': {
                    'get': {'summary': 'Handles GET requests'}
                },
                '/test2/{id}': {
                    'get': {
                        'tags': ['test'],
                        'summary': 'Handles GET requests for another test',
                        'security': ['api_key'],
                        'responses': {
                            '200': {'schema': {'type': 'string'}}
                        }
                    }
                }
            },
            'security_definitions': {
                'api_key': {
                    'type': 'apiKey',
                    'in': 'Header',
                    'name': 'Authorization'
                }
            },
            'definitions': {}
        }
        arguments = argparse.Namespace(app='falcon_app:app', config=None, output=None,
                                       plugin='falcon')
        swagger_part = FalconPy2SwaggerPlugin().run(arguments)
        self.assertDictEqual(expected_result, unordered(swagger_part))

    def test_run_invalid_module(self):
        arguments = argparse.Namespace(app='falcon_invalid_app:app', config=None, output=None,
                                       plugin='falcon')
        self.assertRaises(Py2SwaggerPluginException, FalconPy2SwaggerPlugin().run, arguments)

    def test_run_invalid_app(self):
        arguments = argparse.Namespace(app='falcon_app:invalid_app', config=None, output=None,
                                       plugin='falcon')
        self.assertRaises(Py2SwaggerPluginException, FalconPy2SwaggerPlugin().run, arguments)

    def test_generate_routes(self):
        response = FalconPy2SwaggerPlugin().generate_routes(self.app._router._roots)

        self.assertTrue('/test2/{id}' in next(response))
        self.assertTrue('/test' in next(response))

    def test_set_parser_argument(self):
        parser = argparse.ArgumentParser(description='Process some integers.')
        FalconPy2SwaggerPlugin().set_parser_arguments(parser)
        self.assertEqual(parser._actions[1].dest, 'app')
