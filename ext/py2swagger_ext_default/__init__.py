from importlib import import_module

from py2swagger.plugins import Py2SwaggerPlugin, Py2SwaggerPluginException
from py2swagger.introspector import BaseDocstringIntrospector
from py2swagger.utils import OrderedDict


class DefaultCallbackIntrospector(BaseDocstringIntrospector):
    def get_operation(self):
        """
        Get full swagger operation object

        :return: swagger operation object
        :rtype: OrderedDict
        """

        operation = OrderedDict(
            tags=self.parser.get_tags(),
            summary=self.parser.get_summary(),
            description=self.parser.get_description(),
            parameters=self.parameters,
            produces=None,
            consumes=None,
            responses=self.responses,
            security=self.security
        )

        for key, value in list(operation.items()):
            # Remove empty keys
            if not value:
                operation.pop(key)

        return operation

    def get_security_definitions(self):
        return self.security_definitions


class DefaultApiIntrospector:

    def __init__(self, api_map):
        self.api_map = api_map

    def inspect(self):
        """
        Return part of swagger object. This part contains "paths", "definitions" and "securityDefinitions"
        :return: dict
        """
        paths = {}
        security_definitions = {}
        for path, method, callback in self.api_map:
            if path not in paths:
                paths[path] = {}

            module_name, method_name = callback.rsplit('.', 1)
            module = import_module(module_name)
            callback = getattr(module, method_name)
            callback_introspector = DefaultCallbackIntrospector(callback)
            paths[path][method] = callback_introspector.get_operation()
            security_definitions.update(callback_introspector.get_security_definitions())

        return {
            'paths': paths,
            'definitions': {},
            'securityDefinitions': security_definitions
        }


class DefaultPy2SwaggerPlugin(Py2SwaggerPlugin):

    help = 'Plugin for all applications'

    filtered_methods = ('method_not_allowed', 'on_options')

    def set_parser_arguments(self, parser):
        parser.add_argument('map', help='Path to map. Example: project.settings.test.MAP. '
                                        '\nMap example:'
                                        '\n     MAP = [(path, method, callback), ...]')

    def run(self, arguments, *args, **kwargs):
        module_name, map_name = arguments.map.rsplit('.', 1)
        try:
            m = import_module(module_name)
        except ImportError:
            raise Py2SwaggerPluginException('No module named {}'.format(module_name))

        api_map = getattr(m, map_name, None)
        if api_map is None:
            raise Py2SwaggerPluginException('Invalid api map {}'.format(map_name))

        api_inspector = DefaultApiIntrospector(api_map)
        return api_inspector.inspect()
