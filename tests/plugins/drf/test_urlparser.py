from django.contrib.auth.models import User
from django.conf import settings
from . import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.test import TestCase
from importlib import import_module

from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from py2swagger.plugins.drf.urlparser import UrlParser

from testapp.serializers import CommentSerializer
from testapp.urlparser import MockApiView, NonApiView
from testapp.custom_urlconf import urlpatterns as custom_urlpatterns


class UrlParserTest(TestCase):
    def setUp(self):
        self.url_patterns = patterns(
            '',
            url(r'a-view/$', MockApiView.as_view(), name='a test view'),
            url(r'b-view$', MockApiView.as_view(), name='a test view'),
            url(r'c-view/$', MockApiView.as_view(), name='a test view'),
            url(r'a-view/child/?$', MockApiView.as_view()),
            url(r'a-view/child2/?$', MockApiView.as_view()),
            url(r'another-view/?$', MockApiView.as_view(),
                name='another test view'),
            url(r'view-with-param/(:?<ID>\d+)/?$', MockApiView.as_view(),
                name='another test view'),
            url(r'a-view-honky/?$', MockApiView.as_view(), name='a test view'),
        )
        self.urlparser = UrlParser()

    def test_get_apis(self):
        urls = import_module(settings.ROOT_URLCONF)
        # Overwrite settings with test patterns
        urls.urlpatterns = self.url_patterns
        apis = self.urlparser.get_apis()
        self.assertEqual(self.url_patterns[0], apis[0]['pattern'])
        self.assertEqual('/a-view/', apis[0]['path'])
        self.assertEqual(self.url_patterns[1], apis[1]['pattern'])
        self.assertEqual('/b-view', apis[1]['path'])
        self.assertEqual(self.url_patterns[2], apis[2]['pattern'])
        self.assertEqual('/c-view/', apis[2]['path'])
        self.assertEqual(self.url_patterns[3], apis[3]['pattern'])
        self.assertEqual('/a-view/child/', apis[3]['path'])
        self.assertEqual(self.url_patterns[4], apis[4]['pattern'])
        self.assertEqual('/a-view/child2/', apis[4]['path'])
        self.assertEqual(self.url_patterns[5], apis[5]['pattern'])
        self.assertEqual('/another-view/', apis[5]['path'])
        self.assertEqual(self.url_patterns[6], apis[6]['pattern'])
        self.assertEqual('/view-with-param/{var}/', apis[6]['path'])

    def test_get_apis_urlconf_path(self):
        apis = self.urlparser.get_apis(urlconf='testapp.custom_urlconf')
        self.assertEqual(custom_urlpatterns[0], apis[0]['pattern'])
        self.assertEqual('/a-view/', apis[0]['path'])
        self.assertEqual(custom_urlpatterns[1], apis[1]['pattern'])
        self.assertEqual('/b-view', apis[1]['path'])
        self.assertEqual(custom_urlpatterns[2], apis[2]['pattern'])
        self.assertEqual('/c-view/', apis[2]['path'])
        self.assertEqual(custom_urlpatterns[3], apis[3]['pattern'])
        self.assertEqual('/a-view/child/', apis[3]['path'])
        self.assertEqual(custom_urlpatterns[4], apis[4]['pattern'])
        self.assertEqual('/a-view/child2/', apis[4]['path'])
        self.assertEqual(custom_urlpatterns[5], apis[5]['pattern'])
        self.assertEqual('/another-view/', apis[5]['path'])
        self.assertEqual(custom_urlpatterns[6], apis[6]['pattern'])
        self.assertEqual('/view-with-param/{var}/', apis[6]['path'])

    def test_get_apis_urlconf(self):
        urls = import_module(settings.ROOT_URLCONF)
        # Overwrite settings with test patterns
        urls.urlpatterns = self.url_patterns
        apis = self.urlparser.get_apis(urlconf=urls)
        self.assertEqual(self.url_patterns[0], apis[0]['pattern'])
        self.assertEqual('/a-view/', apis[0]['path'])
        self.assertEqual(self.url_patterns[1], apis[1]['pattern'])
        self.assertEqual('/b-view', apis[1]['path'])
        self.assertEqual(self.url_patterns[2], apis[2]['pattern'])
        self.assertEqual('/c-view/', apis[2]['path'])
        self.assertEqual(self.url_patterns[3], apis[3]['pattern'])
        self.assertEqual('/a-view/child/', apis[3]['path'])
        self.assertEqual(self.url_patterns[4], apis[4]['pattern'])
        self.assertEqual('/a-view/child2/', apis[4]['path'])
        self.assertEqual(self.url_patterns[5], apis[5]['pattern'])
        self.assertEqual('/another-view/', apis[5]['path'])
        self.assertEqual(self.url_patterns[6], apis[6]['pattern'])
        self.assertEqual('/view-with-param/{var}/', apis[6]['path'])

    def test_format_api_patterns(self):
        apis = self.urlparser.get_apis(self.url_patterns)

        self.assertEqual(len(self.url_patterns), len(apis))

    def test_format_api_patterns_url_import(self):
        urls = patterns('', url(r'api/base/path/', include(self.url_patterns)))
        apis = self.urlparser.get_apis(urls)

        self.assertEqual(len(self.url_patterns), len(apis))

    def test_format_api_patterns_with_filter(self):
        apis = self.urlparser.get_apis(self.url_patterns, filter_path="a-view")

        paths = [api['path'] for api in apis]

        self.assertIn("/a-view/", paths)
        self.assertIn("/a-view/child/", paths)
        self.assertIn("/a-view/child2/", paths)
        self.assertIn("/a-view-honky/", paths)

        self.assertEqual(4, len(apis))

    def test_format_api_patterns_excluded_namesapce(self):
        urls = patterns(
            '',
            url(r'api/base/path/',
                include(self.url_patterns, namespace='exclude'))
        )
        apis = self.urlparser.format_api_patterns(
            url_patterns=urls, exclude_namespaces='exclude')

        self.assertEqual([], apis)

    def test_format_api_patterns_url_import_with_routers(self):

        class MockApiViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User
            queryset = User.objects.all()

        class AnotherMockApiViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            model = User
            queryset = User.objects.all()

        router = DefaultRouter()
        router.register(r'other_views', MockApiViewSet, base_name='test_base_name')
        router.register(r'more_views', AnotherMockApiViewSet, base_name='test_base_name')

        urls_app = patterns('', url(r'^', include(router.urls)))
        urls = patterns(
            '',
            url(r'api/', include(urls_app)),
            url(r'test/', include(urls_app))
        )
        apis = self.urlparser.get_apis(urls)

        self.assertEqual(
            4, sum(api['path'].find('api') != -1 for api in apis))
        self.assertEqual(
            4, sum(api['path'].find('test') != -1 for api in apis))

    def test_get_api_callback(self):
        callback = self.urlparser.filter_api_view_callbacks(self.url_patterns[0])
        self.assertTrue(issubclass(callback, MockApiView))

    def test_get_api_callback_not_rest_view(self):
        non_api = patterns(
            '',
            url(r'something', NonApiView.as_view())
        )
        callback = self.urlparser.filter_api_view_callbacks(non_api[0])

        self.assertIsNone(callback)

    def test_assemble_endpoint_data(self):
        """
        Tests that the endpoint data is correctly packaged
        """
        urlparser = UrlParser()
        pattern = self.url_patterns[0]

        data = urlparser.gather_endpoint_data(pattern)

        self.assertEqual(data['path'], '/a-view/')
        self.assertEqual(data['callback'], MockApiView)
        self.assertEqual(data['pattern'], pattern)

    def test_assemble_data_with_non_api_callback(self):
        bad_pattern = patterns('', url(r'^some_view/', NonApiView.as_view()))

        data = self.urlparser.gather_endpoint_data(bad_pattern)

        self.assertIsNone(data)

    def test_exclude_router_api_root(self):
        class MyViewSet(ModelViewSet):
            serializer_class = CommentSerializer
            queryset = User.objects.all()
            model = User

        router = DefaultRouter()
        router.register('test', MyViewSet, base_name='test_base_name')

        urls_created = len(router.urls)

        apis = self.urlparser.get_apis(router.urls)

        self.assertEqual(4, urls_created - len(apis))


class NestedUrlParserTest(TestCase):
    def setUp(self):
        class FuzzyApiView(APIView):
            def get(self, request):
                pass

        class ShinyApiView(APIView):
            def get(self, request):
                pass

        api_fuzzy_url_patterns = patterns(
            '', url(r'^item/$', FuzzyApiView.as_view(), name='find_me'))
        api_shiny_url_patterns = patterns(
            '', url(r'^item/$', ShinyApiView.as_view(), name='hide_me'))

        fuzzy_app_urls = patterns(
            '', url(r'^api/', include(api_fuzzy_url_patterns,
                                      namespace='api_fuzzy_app')))
        shiny_app_urls = patterns(
            '', url(r'^api/', include(api_shiny_url_patterns,
                                      namespace='api_shiny_app')))

        self.project_urls = patterns(
            '',
            url('my_fuzzy_app/', include(fuzzy_app_urls)),
            url('my_shiny_app/', include(shiny_app_urls)),
        )

    def test_exclude_nested_urls(self):
        url_parser = UrlParser()
        # Overwrite settings with test patterns
        urlpatterns = self.project_urls
        apis = url_parser.get_apis(urlpatterns,
                                   exclude_namespaces=['api_shiny_app'])
        self.assertEqual(len(apis), 1)
        self.assertEqual(apis[0]['pattern'].name, 'find_me')
