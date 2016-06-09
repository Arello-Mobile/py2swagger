from django.test import TestCase
from django.conf.urls import patterns
from django.conf.urls import url

from py2swagger.utils import OrderedDict
from py2swagger.plugins.drf.introspectors.method import BaseMethodIntrospector
from py2swagger.plugins.drf.introspectors.view import ApiViewIntrospector, ViewSetIntrospector

from . import REST_FRAMEWORK_V3
from testapp.methods import TestAPIView, TestViewSet
from testapp.serializers import IncludedSerializer


class BaseMethodIntrospectorTestCase(TestCase):
    def setUp(self):
        self.url_patterns = patterns(
            '',
            url(r'a-view$', TestAPIView.as_view()),
            url(r'b-view/(?P<path_parameter>.*)$', TestViewSet.as_view({'get': 'list'})),
        )
        view_introspector_params = {
            'path': '/a-view',
            'callback': self.url_patterns[0].callback.cls,
            'pattern': self.url_patterns[0],
        }
        viewset_introspector_params = {
            'path': '/b-view/{path_parameter}$',
            'callback': self.url_patterns[1].callback.cls,
            'pattern': self.url_patterns[1],
        }

        view_introspector = ApiViewIntrospector(**view_introspector_params)
        viewset_introspector = ViewSetIntrospector(**viewset_introspector_params)

        self.method_introspector = BaseMethodIntrospector(view_introspector, 'get')
        self.method_introspector_empty = BaseMethodIntrospector(view_introspector, 'post')
        self.method_introspector_list = BaseMethodIntrospector(viewset_introspector, 'list')
        self.method_introspector_destroy = BaseMethodIntrospector(view_introspector, 'destroy')

    def test_create_view(self):
        view = self.method_introspector._create_view()
        self.assertTrue(isinstance(view, TestAPIView))

    def test_method_callback(self):
        callback = self.method_introspector._method_callback()
        self.assertTrue(hasattr(callback, '__call__'))

    def test_get_tags(self):
        expected_custom_tags = ['custom_view']
        custom_tags = self.method_introspector._get_tags()
        self.assertEqual(custom_tags, expected_custom_tags)

        expected_empty_tags = [u'test api']
        empty_tags = self.method_introspector_empty._get_tags()
        self.assertEqual(empty_tags, expected_empty_tags)

    def test_get_summary(self):
        expected_custom_summary = 'TestAPIView GET Summary'
        custom_summary = self.method_introspector._get_summary()
        self.assertEqual(custom_summary, expected_custom_summary)

        expected_empty_summary = 'Post Test Api'
        empty_summary = self.method_introspector_empty._get_summary()
        self.assertEqual(empty_summary, expected_empty_summary)

    def test_get_consumes(self):
        expected_consumes = [u'application/json',
                             u'application/x-www-form-urlencoded',
                             u'multipart/form-data']
        consumes = self.method_introspector._get_consumes()
        self.assertEqual(consumes, expected_consumes)

    def test_get_produces(self):
        expected_produces = [u'application/json',
                             u'text/html']
        produces = self.method_introspector._get_produces()
        self.assertEqual(produces, expected_produces)

    def test_get_description(self):
        expected_description = 'Test Description'
        description = self.method_introspector._get_description()
        self.assertEqual(description, expected_description)

    def test_parameters(self):
        # List Method
        if REST_FRAMEWORK_V3:
            expected_list_parameters = ['o', u'limit', u'offset', 'path_parameter']
        else:
            expected_list_parameters = ['o', 'path_parameter']
        list_parameter_names = [p['name'] for p in self.method_introspector_list.parameters]
        self.assertListEqual(list_parameter_names, expected_list_parameters)

        # Method with serializer
        expected_serializer_parameters = ['data']
        serializer_parameter_names = [p['name'] for p in self.method_introspector_empty.parameters]
        self.assertEqual(serializer_parameter_names, expected_serializer_parameters)

    def test_get_path_parameters(self):
        expected_path_parameters = [{'in': 'path', 'name': 'path_parameter', 'required': True, 'type': 'string'}]
        path_parameters = self.method_introspector_list._get_path_parameters()
        self.assertEqual(path_parameters, expected_path_parameters)

    def test_get_parameters(self):
        expected_clean_parameters = []

        clean_parameters = self.method_introspector._get_parameters()
        self.assertEqual(clean_parameters, expected_clean_parameters)

    def test_responses(self):
        expected_empty_responses = OrderedDict([(200, OrderedDict([('description', 'Empty response')]))])
        empty_responses = self.method_introspector.responses
        self.assertEqual(empty_responses, expected_empty_responses)

        serializer_responses = self.method_introspector_empty.responses
        self.assertIn(200, serializer_responses)
        self.assertIn('description', serializer_responses[200])
        self.assertIn('schema', serializer_responses[200])

        list_responses = self.method_introspector_list.responses
        self.assertIn(200, list_responses)
        self.assertIn('description', list_responses[200])
        self.assertIn('schema', list_responses[200])

        expected_destroy_responses = OrderedDict([(204, OrderedDict([('description', 'OK')]))])
        destroy_responses = self.method_introspector_destroy.responses
        self.assertEqual(destroy_responses, expected_destroy_responses)

    def test_get_serializer(self):
        expected_serializers = [IncludedSerializer, IncludedSerializer]
        serializer = self.method_introspector_empty.get_serializers()
        self.assertEqual(serializer, expected_serializers)

    def test_get_view_serializer(self):
        view_serializer = self.method_introspector_list._get_view_serializer()
        if REST_FRAMEWORK_V3:
            self.assertEqual(view_serializer, IncludedSerializer)
        else:
            from rest_framework.pagination import PaginationSerializer
            self.assertEqual(view_serializer, PaginationSerializer)

    def test_get_operation(self):
        expected_keys = sorted(['description', 'produces', 'tags',
                                'summary', 'consumes', 'responses', 'security'])
        operation = self.method_introspector.get_operation()
        self.assertListEqual(sorted(operation.keys()), expected_keys)
