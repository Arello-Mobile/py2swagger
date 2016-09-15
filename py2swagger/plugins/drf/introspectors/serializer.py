from distutils.version import StrictVersion
import inspect
from copy import deepcopy

from py2swagger.utils import OrderedDict
from py2swagger.yamlparser import YAMLDocstringParser
from rest_framework import fields, VERSION as REST_FRAMEWORK_VERSION
from rest_framework.relations import RelatedField
from rest_framework.serializers import BaseSerializer, ModelSerializer

REST_FRAMEWORK_V3 = StrictVersion(REST_FRAMEWORK_VERSION) > StrictVersion('3.0.0')


class SerializerIntrospector(object):
    """
    DjangoRestFramework Serializer Introspector
    """
    DEFAULT_FIELD_TYPE = ('string', 'string', None)

    FIELD_TYPES = {
        # Field Class: (field_type, swagger_type, swagger_format)
        RelatedField: ('related', 'integer', None),
        fields.IntegerField: ('integer', 'integer', None),
        fields.CharField: DEFAULT_FIELD_TYPE,
        fields.FloatField: ('float', 'number', 'double'),
        fields.DateField: ('date', 'string', 'date'),
        fields.DateTimeField: ('datetime', 'string', 'date-time'),
        fields.DecimalField: ('decimal', 'number', 'double'),
        fields.BooleanField: ('boolean', 'boolean', None),
        fields.ChoiceField: ('choice', 'string', None),
        fields.FileField: ('file', 'file', None),
        fields.ImageField: ('image', 'file', None),
        fields.EmailField: ('email', 'string', 'email')
    }

    if REST_FRAMEWORK_V3:
        from rest_framework.fields import MultipleChoiceField
        FIELD_TYPES[MultipleChoiceField] = ('multiple choice', 'string', None)

    def __init__(self, serializer):
        """
        :param serializer: DjangoRestFramework Serializer
        """
        if REST_FRAMEWORK_V3:
            from rest_framework.serializers import ListSerializer
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
                _fields[field_name] = self._prepare_serializer_field(serializer_fields[field_name])

        return _fields

    def _prepare_serializer_field(self, field):
        result = OrderedDict()

        result['required'] = getattr(field, 'required', False)
        result['readOnly'] = getattr(field, 'read_only', False)

        result['response'] = self._get_field_object(field)
        result['request'] = self._get_field_object(field, request=True)

        return result

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
            return self.serializer().get_fields()
        else:
            return self.serializer.get_fields()

    @classmethod
    def _get_field_type(cls, field):
        """
        :param field: DjangoRestFramework field object
        :return: (field_type, swagger_type, swagger_format)
        :rtype: tuple
        """
        for instance in cls.FIELD_TYPES:
            if isinstance(field, instance):
                return cls.FIELD_TYPES[instance]
        return cls.DEFAULT_FIELD_TYPE

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

    @staticmethod
    def _get_default_value(field):
        """
        :param field: DjangoRestFramework field object
        :return: default value for field
        :rtype: any
        """
        default_value = getattr(field, 'default', None)

        if REST_FRAMEWORK_V3:
            from rest_framework.fields import empty
            if default_value == empty:
                default_value = None

        if hasattr(default_value, '__call__'):
            default_value = default_value()

        return default_value

    def _get_field_object(self, field, request=False):
        """
        Creates swagger object for field for request or response

        :param field: DjangoRestFramework field object
        :param request: is this object for request?
        :return: swagger object
        :rtype: OrderedDict
        """
        if isinstance(field, BaseSerializer):
            if getattr(field, 'many', None):
                result = {
                    'type': 'array',
                    'items': SerializerIntrospector(field).build_response_object(),
                }
            else:
                result = SerializerIntrospector(field).build_response_object()
        else:
            field_type, data_type, data_format = self._get_field_type(field)
            if data_type == 'file' and not request:
                data_type = 'string'
            result = OrderedDict(type=data_type)

            # Retrieve Field metadata
            max_val = getattr(field, 'max_value', None)
            min_val = getattr(field, 'min_value', None)
            max_length = getattr(field, 'max_length', None)
            default = self._get_default_value(field)
            description = getattr(field, 'help_text', '')

            if data_format:
                result['format'] = data_format

            if max_val is not None and data_type in ('integer', 'number'):
                result['minimum'] = min_val

            if max_val is not None and data_type in ('integer', 'number'):
                result['maximum'] = max_val

            if max_length is not None and data_type == 'string':
                result['maxLength'] = max_length

            if description:
                result['description'] = description

            if default is not None:
                result['default'] = default

            if field_type in ['multiple choice', 'choice']:
                if isinstance(field.choices, list):
                    result['enum'] = [k for k, v in field.choices]
                elif isinstance(field.choices, dict):
                    # DRF > 3.0.0
                    result['enum'] = [k for k in field.choices]

                if all(isinstance(item, int) for item in result.get('enum', ['1'])):
                    result['type'] = 'integer'
        return result

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
