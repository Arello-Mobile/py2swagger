from unittest import TestCase

from yapsy.IPlugin import IPlugin
from py2swagger.plugins import Py2SwaggerPlugin, Py2SwaggerPluginException


class PluginsTestCase(TestCase):

    def test_plugin_exception(self):
        self.assertTrue(issubclass(Py2SwaggerPluginException, Exception))

    def test_plugin(self):
        self.assertTrue(issubclass(Py2SwaggerPlugin, IPlugin))

        plugin = Py2SwaggerPlugin()

        self.assertEqual('', plugin.summary)
        self.assertEqual('', plugin.description)
        self.assertEqual(None, plugin.set_parser_arguments(None))

        self.assertRaises(NotImplementedError, plugin.run, [])
