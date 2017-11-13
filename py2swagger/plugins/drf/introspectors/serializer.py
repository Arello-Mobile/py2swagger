import inspect
from copy import deepcopy

from py2swagger.utils import OrderedDict
from py2swagger.yamlparser import YAMLDocstringParser
from rest_framework.serializers import ModelSerializer, ListSerializer

from .field import FieldIntrospector


class SerializerIntrospector(object):
    """
    DjangoRestFramework Serializer Introspector
    """

    def __init__(self, serializer):
        """
        :param serializer: DjangoRestFramework Serializer
        """
        if isinstance(serializer, ListSerializer):
            serializer = serializer.child

        self.serializer = serializer
        self.name = self._get_name()

        self.fields = self._collect_fields()

    def _get_name(self):
        """
        :return: Serializer name
        :rtype: str
        """
        serializer = self.serializer

        if inspect.isclass(serializer):
            name = serializer.__name__
        else:
            name = serializer.__class__.__name__

        if name == 'DefaultSerializer' and issubclass(serializer, ModelSerializer):
            model_name = self.serializer.Meta.model.__name__
            name = '{0}Serializer'.format(model_name.strip())
        return name

    def _collect_fields(self):
        serializer_fields = self._get_serializer_fields()
        docstring_fields = self._get_docstring_fields()
        _fields = OrderedDict()

        fields_set = set(serializer_fields.keys()).union(docstring_fields.keys())

        for field_name in fields_set:
            if field_name in docstring_fields:
                field_object = docstring_fields[field_name]
                _fields[field_name] = self._prepare_docstring_field_object(field_object)

            else:
                fi = FieldIntrospector(serializer_fields[field_name], self.__class__)
                _fields[field_name] = fi.prepare_field_object()

        return _fields

    @staticmethod
    def _prepare_docstring_field_object(field_object):
        result = OrderedDict()

        result['required'] = field_object.pop('required', False)
        result['readOnly'] = field_object.pop('readOnly', False)

        if 'response' not in field_object and 'request' not in field_object:
            result['request'] = field_object
            result['response'] = field_object
        else:
            result['request'] = field_object.get('request', field_object.get('response'))
            result['response'] = field_object.get('response', field_object.get('request'))

        return result

    def _get_docstring_fields(self):
        """
        Collect custom serializer fields described in serializer docstring

        :rtype: OrderedDict
        """
        if not inspect.isclass(self.serializer):
            self.serializer = self.serializer.__class__

        parser = YAMLDocstringParser()

        for cls in inspect.getmro(self.serializer):
            parser.update(inspect.getdoc(cls))

        doc_fields = parser.schema.get('fields', OrderedDict())

        return doc_fields

    def _get_serializer_fields(self):
        """
        :return: Serializer fields
        :rtype: dict
        """
        if hasattr(self.serializer, '__call__'):
            return self.serializer().fields.fields
        else:
            return self.serializer.get_fields()

    def _get_formdata_parameters(self):
        """
        Creates formdata parameters

        :return: list of parameters
        :rtype: list
        """
        parameters = []
        for name, field in self.fields.items():
            if field.get('readOnly'):
                continue

            f = deepcopy(field['request'])
            f['required'] = field.get('required')
            f['in'] = 'formData'
            f['name'] = name
            parameters.append(f)
        return parameters

    def _get_body_parameters(self):
        """
        Creates parameters for body

        :return: list of parameters
        :rtype: list
        """
        schema = self._get_schema(request=True)
        schema['schema']['id'] = 'Request{}'.format(schema['schema']['id'])

        schema['in'] = 'body'
        schema['name'] = 'data'
        return [schema]

    def get_parameters(self):
        """
        Creates parameters
        If there are 'file' in parameters returns formData parameters else body parameters

        :return: list of parameters
        :rtype: list
        """
        parameters = self._get_formdata_parameters()
        if any(p.get('type', None) == 'file' for p in parameters):
            return parameters
        else:
            return self._get_body_parameters()

    def _get_schema(self, multiple=False, inline=False, request=False):
        required = []
        properties = OrderedDict()
        schema = OrderedDict()
        if not inline:
            schema['id'] = self.name
        schema['type'] = 'object'

        for field_name, obj in self.fields.items():
            field_object = obj.get('request') if request else obj.get('response')

            if request and (obj.get('readOnly') or field_object.get('readOnly')):
                continue

            if obj.get('required') or field_object.get('required'):
                required.append(field_name)
            properties[field_name] = field_object

        schema['required'] = required
        schema['properties'] = properties

        result = OrderedDict()

        if multiple:
            result['type'] = 'array'
            result['items'] = OrderedDict(schema=schema)
        else:
            result = OrderedDict(schema=schema)

        return result

    def build_response_object(self, multiple=False, inline=False):
        """
        :param multiple: display as array?
        :type multiple: bool
        :param inline: display as inline without id
        :type inline: bool
        :return: full swagger schema for serializer
        :rtype: dict
        """
        return self._get_schema(multiple, inline)
