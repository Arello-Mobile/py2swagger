from django.test import TestCase

from py2swagger.utils import OrderedDict
from py2swagger.plugins.drf.introspectors.serializer import SerializerIntrospector, FieldIntrospector

from testapp.serializers import TestModelSeriazlizer


class SerializerIntrospectorTestCase(TestCase):

    def setUp(self):
        self.serializer = TestModelSeriazlizer()

    def test_prepare_field(self):
        expected_field_obj = OrderedDict([('required', False), ('readOnly', False),
                                          ('response', OrderedDict([('type', 'string'), ('enum', ['a', 'b'])])),
                                          ('request', OrderedDict([('type', 'string'), ('enum', ['a', 'b'])]))])
        field = self.serializer.fields.fields['choices_field']
        self.field_introspector = FieldIntrospector(field, SerializerIntrospector)
        field_obj = self.field_introspector.prepare_field_object()
        self.assertEqual(expected_field_obj, field_obj)

    def test_prepare_field_docstring(self):
        expected_field_obj = OrderedDict(
            [('required', True),
             ('readOnly', False),
             ('response', OrderedDict([('type', 'string')])),
             ('request', OrderedDict([('type', 'array'),
                                      ('items', OrderedDict([('type', 'string')]))]))])

        field = self.serializer.fields.fields['custom_field']
        self.field_introspector = FieldIntrospector(field, SerializerIntrospector)
        field_obj = self.field_introspector.prepare_field_object()
        self.assertEqual(expected_field_obj, field_obj)

