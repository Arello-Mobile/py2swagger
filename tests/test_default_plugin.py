import argparse
from unittest import TestCase

from ext.py2swagger_ext_default import DefaultPy2SwaggerPlugin, DefaultApiIntrospector, DefaultCallbackIntrospector
from py2swagger.plugins import Py2SwaggerPluginException

from tests.default_test_app.map import MAP
from tests.default_test_app import test_method_callback


class DefaultPy2SwaggerPluginTestCase(TestCase):

    def setUp(self):
        pass

    def test_set_parser_argument(self):
        parser = argparse.ArgumentParser(description='Description')
        DefaultPy2SwaggerPlugin().set_parser_arguments(parser)
        self.assertEqual(parser._actions[1].dest, 'map')

    def test_run(self):
        arguments = argparse.Namespace(map='tests.default_test_app.map.MAP')
        plugin = DefaultPy2SwaggerPlugin()
        swagger_part = plugin.run(arguments)
        self.assertEqual(3, len(swagger_part.keys()))
        self.assertIn('paths', swagger_part)
        self.assertIn('securityDefinitions', swagger_part)
        self.assertIn('definitions', swagger_part)

    def test_run_invalid_module(self):
        arguments = argparse.Namespace(map='invalid.path.to_map')
        self.assertRaises(Py2SwaggerPluginException, DefaultPy2SwaggerPlugin().run, arguments)

    def test_run_invalid_map(self):
        arguments = argparse.Namespace(map='tests.default_test_app.map.INVALID_MAP')
        self.assertRaises(Py2SwaggerPluginException, DefaultPy2SwaggerPlugin().run, arguments)


class DefaultApiIntrospectorTestCase (TestCase):

    def test_inspect(self):
        swagger_part = DefaultApiIntrospector(MAP).inspect()
        self.assertEqual(3, len(swagger_part.keys()))
        self.assertIn('paths', swagger_part)
        self.assertIn('securityDefinitions', swagger_part)
        self.assertIn('definitions', swagger_part)


class DefaultCallbackIntrospectorTestCase(TestCase):

    def setUp(self):
        self.introspector = DefaultCallbackIntrospector(test_method_callback)

    def test_get_operation(self):
        expected_keys = sorted(['tags', 'summary', 'security', 'responses'])
        operation = self.introspector.get_operation()
        self.assertListEqual(expected_keys, sorted(operation.keys()))

    def test_get_security_definitions(self):
        security_definitions = self.introspector.get_security_definitions()
        self.assertIn('test_token', security_definitions)
