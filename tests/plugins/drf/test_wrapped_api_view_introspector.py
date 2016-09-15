from django.test import TestCase
from . import patterns
from django.conf.urls import url

from py2swagger.plugins.drf.introspectors.view import WrappedApiViewIntrospector
from py2swagger.plugins.drf.introspectors.method import WrappedApiViewMethodIntrospector

from testapp.views import decorator_view


class WrappedApiViewIntrospectorTestCase(TestCase):
    def setUp(self):
        self.url_patterns = patterns(
            '',
            url(r'c-view$', decorator_view),
        )

        decorator_api_url_object = {
            'path': '/c-view',
            'callback': self.url_patterns[0].callback.cls,
            'pattern': self.url_patterns[0],
        }

        self.introspector = WrappedApiViewIntrospector(**decorator_api_url_object)

    def test_methods(self):
        methods = self.introspector.methods()
        for method in methods:
            self.assertTrue(isinstance(method, WrappedApiViewMethodIntrospector))
