from django.test import TestCase
from . import patterns

from django.conf.urls import url

from py2swagger.plugins.drf.introspectors.view import ApiViewIntrospector
from py2swagger.plugins.drf.introspectors.method import ApiViewMethodIntrospector

from testapp.views import EmailApiView


class ApiViewIntrospectorTestCase(TestCase):
    def setUp(self):
        self.url_patterns = patterns(
            '',
            url(r'a-view$', EmailApiView.as_view()),
        )

        email_api_url_object = {
            'path': '/a-view',
            'callback': self.url_patterns[0].callback.cls,
            'pattern': self.url_patterns[0],
        }

        self.introspector = ApiViewIntrospector(**email_api_url_object)

    def test_methods(self):
        methods = self.introspector.methods()
        for method in methods:
            self.assertTrue(isinstance(method, ApiViewMethodIntrospector))
