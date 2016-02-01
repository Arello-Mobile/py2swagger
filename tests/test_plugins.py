from unittest import TestCase

from yapsy.IPlugin import IPlugin
from py2swagger import plugins


class PluginsTestCase(TestCase):

    def test_plugin_exception(self):
        self.assertTrue(issubclass(plugins.Py2SwaggerPluginException, Exception))

    def test_plugin(self):
        self.assertTrue(issubclass(plugins.Py2SwaggerPlugin, IPlugin))

        plugin = plugins.Py2SwaggerPlugin()

        self.assertEqual('', plugin.help)
        self.assertEqual(None, plugin.set_parser_arguments(None))

        self.assertRaises(NotImplementedError, plugin.run, [])
