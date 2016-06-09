import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.utils.functional import Promise
from py2swagger.utils import OrderedDict

from .serializer import SerializerIntrospector
from .view import get_view_introspector


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class ApiIntrospector(object):
    """
    Inspect apis found by url parser
    """

    def __init__(self, apis):
        self.apis = apis
        self.serializers = []
        self.security_definitions = {}

    def inspect(self):
        """
        Prepare part of Open Api object with contains "paths", "definitions" and "securityDefinitions"

        :return: swagger_part
        :rtype: dict
        """

        swagger_part = dict()
        # Calling First
        swagger_part['paths'] = self.get_paths()

        swagger_part['definitions'] = self.get_definitions()
        swagger_part['securityDefinitions'] = self.security_definitions
        return swagger_part

    def get_paths(self):
        """
        Prepare OpenApi "Paths Object" with all paths found in api

        :return: paths
        :rtype: dict
        """
        paths = dict()
        for api in self.apis:
            view_introspector = get_view_introspector(api)
            for method_introspector in view_introspector:
                if method_introspector.http_method.lower() == 'options':
                    continue

                self.serializers.extend(method_introspector.get_serializers())
                self.security_definitions.update(method_introspector.get_security_definitions())

                if method_introspector.introspector.path not in paths:
                    paths[method_introspector.introspector.path] = {}

                paths[method_introspector.introspector.path][method_introspector.http_method.lower()] = \
                    json.loads(json.dumps(method_introspector.get_operation(), cls=LazyEncoder))
        return paths

    def get_definitions(self):
        """
        Return all serializer definitions found in api

        :return: definitions
        :rtype: dict
        """
        definitions = OrderedDict()
        for serializer in set(self.serializers):
            si = SerializerIntrospector(serializer)
            definitions[si.name] = si.build_response_object(inline=True)['schema']

        # tricky dumps and loads for django specific fields
        return json.loads(json.dumps(definitions, cls=LazyEncoder))
