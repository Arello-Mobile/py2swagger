from django.test import TestCase
from django.conf.urls import patterns
from django.conf.urls import url

from py2swagger.plugins.drf.introspectors.view import ApiViewIntrospector
from py2swagger.plugins.drf.introspectors.method import ApiViewMethodIntrospector
from py2swagger.utils import load_class

from testapp.views import EmailApiView
from testapp.serializers import TestModelSeriazlizer


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

        view_introspector = ApiViewIntrospector(**email_api_url_object)
        self.method_introspector = ApiViewMethodIntrospector(view_introspector, 'post')

    def test_methods(self):
        actual = load_class('testapp.serializers.TestModelSeriazlizer')
        self.assertEqual(actual, TestModelSeriazlizer)
