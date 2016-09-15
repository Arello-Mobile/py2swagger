from importlib import import_module

from py2swagger.plugins import Py2SwaggerPlugin, Py2SwaggerPluginException
from py2swagger.introspector import BaseDocstringIntrospector
from py2swagger.utils import OrderedDict


class FalconMethodIntrospector(BaseDocstringIntrospector):
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


class FalconPy2SwaggerPlugin(Py2SwaggerPlugin):

    help = 'Plugin for Falcon Framework applications'

    filtered_methods = ('method_not_allowed', 'on_options')

    def set_parser_arguments(self, parser):
        parser.add_argument('app', help='Falcon application. Example: project.api:app')

    def run(self, arguments, *args, **kwargs):
        module_name, application_name = arguments.app.split(':', 1)
        try:
            m = import_module(module_name)
        except ImportError:
            raise Py2SwaggerPluginException('No module named {}'.format(module_name))

        app = getattr(m, application_name, None)
        if app is None or not hasattr(app, '_router'):
            raise Py2SwaggerPluginException('Invalid Falcon application {}'.format(application_name))

        paths = {}
        security_definitions = {}
        for path, method_map in self.generate_routes(app._router._roots):
            if path not in paths:
                paths[path] = {}
            for method in method_map:
                f = method_map[method]
                if hasattr(f, '__self__') and f.__name__ not in self.filtered_methods:
                    method_introspector = FalconMethodIntrospector(f)
                    operation = method_introspector.get_operation()
                    paths[path][method.lower()] = operation
                    security_definitions.update(method_introspector.get_security_definitions())

        swagger_part = {
            'paths': paths,
            'definitions': {},
            'security_definitions': security_definitions
        }
        return swagger_part

    def generate_routes(self, nodes, path=''):
        for node in nodes:
            node_path = '{}/{}'.format(path, node.raw_segment)
            if node.children:
                for item in self.generate_routes(node.children, node_path):
                    yield item
            else:
                yield (node_path, node.method_map)
