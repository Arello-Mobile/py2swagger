import six

from py2swagger.plugins import Py2SwaggerPlugin, Py2SwaggerPluginException
from py2swagger.introspector import BaseDocstringIntrospector
from py2swagger.utils import OrderedDict, load_class


class SimplePlugin(Py2SwaggerPlugin):

    summary = 'Plugin for all applications'
    description = 'Parse schemas from configuration file. Add to your config:\n'\
                  'PLUGIN_SETTINGS[\'endpoints\'] = [(path, method, callback), ...]'

    def __init__(self):
        super(SimplePlugin, self).__init__()
        self._paths = {}
        self._security_definitions = {}

    @staticmethod
    def _operation(introspector):
        operation = OrderedDict(
            tags=introspector.tags,
            summary=introspector.parser.get_summary(),
            description=introspector.parser.get_description(),
            parameters=introspector.parameters,
            responses=introspector.responses,
            security=introspector.security
        )

        # Remove empty keys
        for key, value in list(operation.items()):
            if not value:
                operation.pop(key)

        return operation

    def _add_operation(self, path, method, introspector):
        if path not in self._paths:
            self._paths[path] = {}
        self._paths[path][method] = self._operation(introspector)

    def _add_security_definitions(self, introspector):
        self._security_definitions.update(introspector.security_definitions)

    def _introspect(self, path, method, callback):
        introspector = BaseDocstringIntrospector(callback)
        self._add_operation(path, method, introspector)
        self._add_security_definitions(introspector)

    def run(self, arguments, endpoints=None, *args, **kwargs):
        """
        Return part of swagger object. This part contains "paths", "definitions" and "securityDefinitions"
        :return: dict
        """
        if endpoints is None:
            raise Py2SwaggerPluginException('Configuration is missed. Please add PLUGIN_SETTINGS[\'endpoints\'] to your '
                                            'configuration file.')

        for path, method, callback in endpoints:
            if isinstance(callback, six.string_types):
                callback = load_class(callback)
            self._introspect(path, method, callback)

        return {
            'paths': self._paths,
            'securityDefinitions': self._security_definitions
        }
