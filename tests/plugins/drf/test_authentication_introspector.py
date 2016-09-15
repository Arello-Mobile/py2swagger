from django.test import TestCase
from py2swagger.utils import OrderedDict

from py2swagger.plugins.drf.introspectors.authentication import BasicAuthenticationIntrospector, \
    TokenAuthenticationIntrospector, get_authentication_introspectors

from testapp.authenticators import TestBasicAuthView, TestTokenAuthView, TestGetAuthIntrospectorsView


class BasicAuthenticationIntrospectorTestCase(TestCase):

    def test_security(self):
        expected_result = [OrderedDict([('basic_authentication', [])])]

        instance = TestBasicAuthView()
        introspector = BasicAuthenticationIntrospector(instance)
        self.assertEqual(expected_result, introspector.security)

    def test_security_definitions(self):
        expected_result = OrderedDict([
            ('basic_authentication', {
                'type': 'basic',
                'description': 'Clients should authenticate by passing the base64 encoded username:password string\n'
                               '                in the "Authorization HTTP header, prepended with the string "Basic ".\n'
                               '                For example:\n                    Authorization: Basic dXNlcjpwYXNzd29yZA=='
            })
        ])

        instance = TestBasicAuthView()
        introspector = BasicAuthenticationIntrospector(instance)
        self.assertEqual(expected_result, introspector.security_definitions)


class TokenAuthenticationIntrospectorTestCase(TestCase):

    def test_security(self):
        expected_result = [
            OrderedDict([('djangorestframework_token_authentication', [])])
        ]

        instance = TestTokenAuthView()
        introspector = TokenAuthenticationIntrospector(instance)
        self.assertEqual(expected_result, introspector.security)

    def test_security_definitions(self):
        expected_result = OrderedDict([
            ('djangorestframework_token_authentication', {
                'description': 'Clients should authenticate by passing the token key in the "Authorization"\n'
                               '                HTTP header, prepended with the string "Token ".  For example:\n'
                               '                Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a',
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header'
            })
        ])

        instance = TestTokenAuthView()
        introspector = TokenAuthenticationIntrospector(instance)
        self.assertEqual(expected_result, introspector.security_definitions)


class AuthenticationIntrospectorMethodsTestCase(TestCase):

    def test_get_introspectors(self):
        instance = TestGetAuthIntrospectorsView()
        introspectors = get_authentication_introspectors(instance)

        self.assertTrue(isinstance(introspectors[0], BasicAuthenticationIntrospector))
        self.assertTrue(isinstance(introspectors[1], TokenAuthenticationIntrospector))
