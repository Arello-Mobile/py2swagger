from django.test import TestCase
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from py2swagger.utils import OrderedDict

from py2swagger.plugins.drf.introspectors.filter import DjangoFilterBackendIntrospector, \
    OrderingFilterBackendIntrospector, get_filter_introspectors

from testapp.filters import TestDjangoFilterBackendView, TestOrderingFilterView, \
    TestGetFilterIntrospectorsView


class DjangoFilterBackendIntrospectorTestCase(TestCase):

    def test_parameters(self):
        expected_result = [
            OrderedDict({
                'in': 'query',
                'name': 'test_filter_field_1',
                'type': 'string',
                'required': False,
                'description': 'Filter parameter',
            }),
            OrderedDict({
                'in': 'query',
                'name': 'test_filter_field_2',
                'type': 'string',
                'required': False,
                'description': 'Filter parameter',
            }),
            OrderedDict({
                'in': 'query',
                'name': 'o',
                'type': 'string',
                'description': 'Ordering parameter',
                'enum': ['test_filter_field_1', 'test_filter_field_2', '-test_filter_field_1', '-test_filter_field_2'],
            }),
        ]

        instance = TestDjangoFilterBackendView()
        introspector = DjangoFilterBackendIntrospector(instance, DjangoFilterBackend)

        self.assertEqual(sorted(expected_result[0]), sorted(introspector.parameters[0]))
        self.assertEqual(sorted(expected_result[1]), sorted(introspector.parameters[1]))
        self.assertEqual(sorted(expected_result[2]), sorted(introspector.parameters[2]))


class OrderingFilterBackendIntrospectorTestCase(TestCase):

    def test_parameters(self):
        expected_result = [OrderedDict({
            'in': 'query',
            'name': u'ordering',
            'type': 'string',
            'enum': ('test_filter_field_1', 'test_filter_field_2'),
        })]

        instance = TestOrderingFilterView()
        introspector = OrderingFilterBackendIntrospector(instance, OrderingFilter)

        self.assertEqual(expected_result, introspector.parameters)


class FilterIntrospectorMethodsTestCase(TestCase):

    def test_get_introspectos(self):
        instance = TestGetFilterIntrospectorsView()
        introspectors = get_filter_introspectors(instance)

        self.assertTrue(isinstance(introspectors[0], DjangoFilterBackendIntrospector))
        self.assertTrue(isinstance(introspectors[1], OrderingFilterBackendIntrospector))

