import inspect

from rest_framework import fields
from rest_framework.relations import RelatedField
from rest_framework.serializers import BaseSerializer

from py2swagger.utils import OrderedDict
from py2swagger.yamlparser import YAMLDocstringParser

from . import REST_FRAMEWORK_V3


class FieldIntrospector(object):
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

    _field = None
    _serializer_inrospector_class = None

    def __init__(self, field, serializer_inrospector_class):
        self._field = field
        self._serializer_inrospector_class = serializer_inrospector_class

    def prepare_field_object(self):
        request, response = self._prepare_form_docstring()
        result = OrderedDict()

        result['required'] = getattr(self._field, 'required', False)
        result['readOnly'] = getattr(self._field, 'read_only', False)

        result['response'] = response or self._get_field_object()
        result['request'] = request or self._get_field_object(request=True)

        return result

    def _prepare_form_docstring(self):
        parser = YAMLDocstringParser()

        for cls in inspect.getmro(self._field.__class__):
            parser.update(inspect.getdoc(cls))

        return parser.schema.get('request'), \
               parser.schema.get('response')

    def _get_field_object(self, request=False):
        """
        Creates swagger object for field for request or response

        :param request: is this object for request?
        :return: swagger object
        :rtype: OrderedDict
        """
        if isinstance(self._field, BaseSerializer):
            if getattr(self._field, 'many', None):
                result = {
                    'type': 'array',
                    'items': self._serializer_inrospector_class(self._field).build_response_object(),
                }
            else:
                result = self._serializer_inrospector_class(self._field).build_response_object()
        else:
            field_type, data_type, data_format = self._get_field_type(self._field)
            if data_type == 'file' and not request:
                data_type = 'string'
            result = OrderedDict(type=data_type)

            # Retrieve Field metadata
            max_val = getattr(self._field, 'max_value', None)
            min_val = getattr(self._field, 'min_value', None)
            max_length = getattr(self._field, 'max_length', None)
            default = self._get_default_value()
            description = getattr(self._field, 'help_text', '')

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
                if isinstance(self._field.choices, list):
                    result['enum'] = [k for k, v in self._field.choices]
                elif isinstance(self._field.choices, dict):
                    # DRF > 3.0.0
                    result['enum'] = [k for k in self._field.choices]

                if all(isinstance(item, int) for item in result.get('enum', ['1'])):
                    result['type'] = 'integer'
        return result

    def _get_default_value(self):
        """
        :return: default value for field
        :rtype: any
        """
        default_value = getattr(self._field, 'default', None)

        if REST_FRAMEWORK_V3:
            from rest_framework.fields import empty
            if default_value == empty:
                default_value = None

        if hasattr(default_value, '__call__'):
            default_value = default_value()

        return default_value

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
