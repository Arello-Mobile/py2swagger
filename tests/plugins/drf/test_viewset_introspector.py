from django.test import TestCase
from django.conf.urls import patterns
from django.conf.urls import url

from py2swagger.plugins.drf.introspectors.view import ViewSetIntrospector
from py2swagger.plugins.drf.introspectors.method import ViewSetMethodIntrospector

from testapp.views import CustomViewSet


class ViewsetIntrospectorTestCase(TestCase):
    def setUp(self):
        self.url_patterns = patterns(
            '',
            url(r'b-view$', CustomViewSet.as_view({'get': 'retrieve'})),
        )

        custom_viewset_api_url_object = {
            'path': '/b-view',
            'callback': self.url_patterns[0].callback.cls,
            'pattern': self.url_patterns[0],
        }

        self.introspector = ViewSetIntrospector(**custom_viewset_api_url_object)

    def test_methods(self):
        methods = self.introspector.methods()
        for method in methods:
            self.assertTrue(isinstance(method, ViewSetMethodIntrospector))
