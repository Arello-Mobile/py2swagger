import argparse
import codecs
import imp
import logging
import os
import sys
import json

from distutils.sysconfig import get_python_lib
from yapsy.PluginManager import PluginManager

from .config import SWAGGER_SETTINGS, API_SETTINGS
from .plugins import Py2SwaggerPlugin, Py2SwaggerPluginException
from .schema_builder import SchemaBuilder
from .utils import update_settings


logging.basicConfig(level=logging.INFO)


def run():  # pragma: no cover
    internal_ext_path = os.path.join(os.path.dirname(__file__), '../ext')
    swagger_settings = SWAGGER_SETTINGS.copy()
    # search plugins in virtualenv site packages
    plugin_manager = PluginManager(
        categories_filter={'py2swagger': Py2SwaggerPlugin},
        directories_list=[internal_ext_path, get_python_lib()],
        plugin_info_ext='py2swagger'
    )
    plugin_manager.collectPlugins()

    parser = argparse.ArgumentParser(description='Swagger schema builder')
    parser.add_argument('-c', '--config', action='store', dest='config', help='Path to config file')
    parser.add_argument('-o', '--output', action='store', dest='output', help='Output file (Default stdout)')

    sub_parsers = parser.add_subparsers(title='plugins', dest='plugin')

    # set arguments from plugins
    for plugin in plugin_manager.getAllPlugins():
        sub_parser = sub_parsers.add_parser(
            plugin.name, help=plugin.plugin_object.help)
        plugin.plugin_object.set_parser_arguments(sub_parser)

    sys.path.append(os.getcwd())
    args = parser.parse_args()

    plugin = plugin_manager.getPluginByName(args.plugin, category='py2swagger')
    if not plugin:
        sys.stderr.write('Plugin not available\n')
        sys.exit(1)

    if args.config:
        custom_config = imp.load_source('config', args.config)
        custom_swagger_settings = getattr(custom_config, 'SWAGGER_SETTINGS', dict())
        api_settings = getattr(custom_config, 'API_SETTINGS', dict())
        swagger_settings.update(custom_swagger_settings)
        API_SETTINGS.update(api_settings)

    try:
        swagger_settings_part = plugin.plugin_object.run(args, **API_SETTINGS)
    except Py2SwaggerPluginException as e:
        sys.stderr.write('{}\n'.format(e))
        sys.exit(1)

    swagger_settings = update_settings(swagger_settings, swagger_settings_part)
    builder = SchemaBuilder(**swagger_settings)

    swagger_schema = json.dumps(builder.schema, indent=2)
    if args.output:
        with codecs.open(args.output, 'wb', encoding='utf-8') as f:
            f.write(swagger_schema)
    else:
        sys.stdout.write(swagger_schema)


if __name__ == '__main__':
    run()
