from django.test import TestCase
from django.conf.urls import patterns
from django.conf.urls import url
from rest_framework import routers

from py2swagger.plugins.drf.injection import viewset_as_view_decorator
from py2swagger.plugins.drf.urlparser import UrlParser
from py2swagger.plugins.drf.introspectors.api import ApiIntrospector
from py2swagger.plugins.drf.introspectors.view import ApiViewIntrospector, ViewSetIntrospector, WrappedApiViewIntrospector, get_view_introspector

from testapp.views import EmailApiView, CustomViewSet, decorator_view, RedefineViewSet


class ApiIntrospectorMixin(object):
    def test_inspect(self):
        swagger_part = self.api_introspector.inspect()
        self.assertEqual(3, len(swagger_part))
        self.assertIn('paths', swagger_part)
        self.assertIn('definitions', swagger_part)
        self.assertIn('securityDefinitions', swagger_part)

    def test_get_definitions(self):
        result = self.api_introspector.get_definitions()
        self.assertEqual(1, len(result.keys()))
        self.assertIn('TestModelSeriazlizer', result)


class ApiIntrospectorTestCase(TestCase, ApiIntrospectorMixin):
    def setUp(self):
        CustomViewSet.as_view = viewset_as_view_decorator(CustomViewSet.as_view)
        self.url_patterns = patterns(
            '',
            url(r'a-view$', EmailApiView.as_view()),
            url(r'b-view$', CustomViewSet.as_view({'get': 'list'})),
            url(r'c-view$', decorator_view),
        )

        url_parser = UrlParser()
        self.apis = url_parser.get_apis(url_patterns=self.url_patterns)
        self.api_introspector = ApiIntrospector(self.apis)
        self.api_introspector.inspect()

    def test_get_introspector(self):
        # ApiView
        introspector = get_view_introspector(self.apis[0])
        self.assertTrue(isinstance(introspector, ApiViewIntrospector), 'Invalid introspector instance')

        introspector = get_view_introspector(self.apis[1])
        self.assertTrue(isinstance(introspector, ViewSetIntrospector), 'Invalid introspector instance')

        introspector = get_view_introspector(self.apis[2])
        self.assertTrue(isinstance(introspector, WrappedApiViewIntrospector), 'Invalid introspector instance')


class ContentIntrospectorTestCase(TestCase, ApiIntrospectorMixin):
    def setUp(self):
        RedefineViewSet.as_view = viewset_as_view_decorator(RedefineViewSet.as_view)
        router = routers.SimpleRouter()
        router.register(r'd-view$', RedefineViewSet, base_name='test_base_name')
        self.url_patterns = router.urls

        url_parser = UrlParser()
        self.apis = url_parser.get_apis(url_patterns=self.url_patterns)
        self.api_introspector = ApiIntrospector(self.apis)
        self.api_introspector.inspect()

    def test_content(self):
        content = [
            'new_custom_field1',
            'new_custom_field2',
            'new_custom_field3'
        ]

        for path in self.api_introspector.get_paths().values():
            for operation in path.values():
                resp = operation.get('responses', None)
                if not resp:
                    self.assertRaises(Exception, msg='Field \"responses\" not exist')

                for c, r in resp.items():
                    if u'Redefined response method' == r.get('description'):
                        try:
                            item = list(r['schema']['allOf'][1]['properties'].keys())
                        except KeyError as e:
                            raise Exception('Inconsistent data in datamap', e)
                        content.pop(content.index(item[0]))

        self.assertEqual([], content)

