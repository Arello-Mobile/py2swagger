from django.test import TestCase
from rest_framework import VERSION

from distutils.version import StrictVersion
from py2swagger.plugins.drf.introspectors.serializer import SerializerIntrospector

from testapp.serializers import TestModelSeriazlizer


class SerializerIntrospectorTestCase(TestCase):

    def setUp(self):
        self.serializer_introspector = SerializerIntrospector(TestModelSeriazlizer)

        self.fields = [
            'related_models',
            'related_model',
            'custom_field',
            'custom_integer_field',
            'id',
            'datetime_field',
            'date_field',
            'time_field',
            'char_field',
            'choices_field',
            'text_field',
            'decimal_field',
            'float_field',
            'integer_field',
            'boolean_field',
            'file_field',
            'related_field',
            'parent_field',
        ]

        self.readonly_fields = [
            'id'
        ]

        self.not_required_field = [
            'decimal_field',
            'integer_field',
            'boolean_field',
            'custom_integer_field'
        ]

        if StrictVersion(VERSION) >= StrictVersion('3.0.0'):
            self.not_required_field.append('choices_field')

        self.field_types = {
            'related_models': ('array', None),
            'related_model': (None, None),
            'custom_integer_field': ('integer', None),
            'custom_field': ('array', None),
            'id': ('integer', None),
            'datetime_field': ('string', 'date-time'),
            'date_field': ('string', 'date'),
            'time_field': ('string', None),
            'char_field': ('string', None),
            'choices_field': ('string', None),
            'text_field': ('array', None),
            'float_field': ('number', 'double'),
            'decimal_field': ('number', 'double'),
            'integer_field': ('integer', None),
            'boolean_field': ('boolean', None),
            'file_field': ('file', None),
            'related_field': ('integer', None),
            'parent_field': ('integer', None)
        }

    def get_field_type(self, field_name):
        field = self.get_field_object(field_name, True)
        _, data_type, data_format = None, field.get('type'), field.get('format', None)
        return data_type, data_format

    def get_default_value(self, field_name, request=False):
        return self.get_field_object(field_name, request).get('default')

    def get_field_object(self, field_name, request=False):
        key = 'request' if request else 'response'
        return self.serializer_introspector.fields.get(field_name, {}).get(key, {})

    def test_name(self):
        self.assertEqual(self.serializer_introspector.name, 'TestModelSeriazlizer')

    def test_fields(self):
        fields = self.serializer_introspector.fields

        self.assertEqual(len(self.fields), len(fields))

        for field in self.fields:
            self.assertIn(field, fields)

    def test_readonly_fields(self):

        readonly_fields = []
        for k, v in self.serializer_introspector.fields.items():
            if v.get('readOnly'):
                readonly_fields.append(k)

        self.assertEqual(len(self.readonly_fields), len(readonly_fields))

        for field in self.readonly_fields:
            self.assertIn(field, readonly_fields)

    def test_field_types(self):
        for field in self.fields:
            field_type = self.field_types.get(field)
            self.assertEqual(field_type, self.get_field_type(field))

    def test_paramters(self):
        parameters = self.serializer_introspector.get_parameters()
        self.assertEqual(len(self.fields) - len(self.readonly_fields), len(parameters))

    def test_required_fields(self):
        required_fields = []

        for k, v in self.serializer_introspector.fields.items():
            if v.get('required') or v['response'].get('required') or v['request'].get('required'):
                required_fields.append(k)

        for field in self.fields:
            if field in self.not_required_field or field in self.readonly_fields:
                self.assertNotIn(field, required_fields)
            else:
                self.assertIn(field, required_fields)

    def test_properties(self):
        self.assertEqual(len(self.fields), len(self.serializer_introspector.fields))

    def test_default_values(self):

        field_name = 'custom_integer_field'
        self.assertEqual(5, self.get_default_value(field_name, True))
        self.assertEqual(5, self.get_default_value(field_name))

        if StrictVersion(VERSION) >= StrictVersion('3.0.0'):
            return

        field_name = 'boolean_field'
        self.assertEqual(False, self.get_default_value(field_name, True))
        self.assertEqual(False, self.get_default_value(field_name))

        field_name = 'choices_field'
        self.assertEqual('a', self.get_default_value(field_name, True))
        self.assertEqual('a', self.get_default_value(field_name))

        field_name = 'decimal_field'
        self.assertEqual(100.0, self.get_default_value(field_name, True))
        self.assertEqual(100.0, self.get_default_value(field_name))

        field_name = 'integer_field'
        self.assertEqual(0, self.get_default_value(field_name, True))
        self.assertEqual(0, self.get_default_value(field_name))

    def test_choices(self):
        choices_field = self.serializer_introspector.fields.get('choices_field')['request']
        self.assertTrue('enum' in choices_field)
        self.assertEqual(choices_field['enum'], ['a', 'b'])

    def test_max_length(self):
        field = self.get_field_object('char_field')
        self.assertTrue('maxLength' in field)
        self.assertEqual(field['maxLength'], 50)

    def test_min_max(self):
        field = self.get_field_object('custom_integer_field')

        self.assertTrue('minimum' in field)
        self.assertEqual(field['minimum'], 0)

        self.assertTrue('maximum' in field)
        self.assertEqual(field['maximum'], 10)

    def test_field_description(self):
        field = self.get_field_object('datetime_field')
        self.assertEqual(field['description'], 'Date time field')

        field = self.get_field_object('file_field')
        self.assertEqual(field['description'], 'File field')

    def test_serializer_instance(self):
        serializer = TestModelSeriazlizer()
        serializer_introspector = SerializerIntrospector(serializer)

        self.assertEqual(serializer_introspector.name, 'TestModelSeriazlizer')

    def test_response_object(self):
        response = self.serializer_introspector.build_response_object()

        self.assertIn('schema', response)

    def test_inline_response_object(self):
        response = self.serializer_introspector.build_response_object(inline=True)

        self.assertIn('schema', response)
        self.assertNotIn('id', response['schema'])

    def test_multiple_response_object(self):
        response = self.serializer_introspector.build_response_object(multiple=True)

        self.assertNotIn('schema', response)
        self.assertIn('items', response)
        self.assertEqual(response['type'], 'array')

    def test_docstring_fields(self):

        self.assertIn('text_field', self.serializer_introspector.fields)
        self.assertEqual(self.serializer_introspector.fields['text_field']['request']['type'], 'array')

    def test_default_serializer(self):
        if StrictVersion(VERSION) >= StrictVersion('3.0.0'):
            return

        from rest_framework.viewsets import ModelViewSet
        from django.http import HttpRequest
        from testapp.models import TestModel

        class TestViewSet(ModelViewSet):
            model = TestModel

        view = TestViewSet()
        view.request = HttpRequest()

        si = SerializerIntrospector(view.get_serializer_class())

        self.assertEqual(si.name, 'TestModelSerializer')
