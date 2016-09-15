import argparse
import codecs
import logging
import os
import sys
import json

from yapsy.PluginManager import PluginManager

from .plugins import Py2SwaggerPlugin, Py2SwaggerPluginException
from .schema_builder import SchemaBuilder
from .utils import get_settings, update_settings


logging.basicConfig(level=logging.INFO)


def _get_project_root_path(project_root_path=None, local_config_file_path=None):
    if project_root_path:
        return project_root_path

    if local_config_file_path:
        return os.path.dirname(local_config_file_path)

    return os.getcwd()


def run():  # pragma: no cover
    plugin_manager = PluginManager(
        categories_filter={'py2swagger': Py2SwaggerPlugin},
        directories_list=[os.path.join(os.path.dirname(__file__), 'plugins')],
        plugin_info_ext='py2swagger'
    )
    plugin_manager.collectPlugins()

    parser = argparse.ArgumentParser(description='Swagger schema builder')
    parser.add_argument('-c', '--config', action='store', dest='config', help='Path to config file')
    parser.add_argument('-r', '--root', action='store', dest='root', help='Path to project root. Default is current directory or configuration file location')
    parser.add_argument('-o', '--output', action='store', dest='output', help='Output file (Default stdout)')

    sub_parsers = parser.add_subparsers(title='plugins', dest='plugin')

    # set arguments from plugins
    for plugin in plugin_manager.getAllPlugins():
        sub_parser = sub_parsers.add_parser(plugin.name,
                                            help=plugin.plugin_object.summary,
                                            description=plugin.plugin_object.description)
        plugin.plugin_object.set_parser_arguments(sub_parser)

    args = parser.parse_args()

    sys.path.append(_get_project_root_path(args.root, args.config))

    swagger_settings, plugin_settings = get_settings(args.config)

    plugin = plugin_manager.getPluginByName(args.plugin, category='py2swagger')
    if not plugin:
        sys.stderr.write('Plugin not available\n')
        sys.exit(1)

    try:
        swagger_settings_part = plugin.plugin_object.run(args, **plugin_settings)
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
