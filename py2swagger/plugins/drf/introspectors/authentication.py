from abc import ABCMeta

from py2swagger.introspector import BaseDocstringIntrospector
from py2swagger.utils import OrderedDict


class BaseAuthenticationIntrospector(BaseDocstringIntrospector):
    """
    Collects information from authentication classes
    """

    __metaclass__ = ABCMeta
    name = None


class BasicAuthenticationIntrospector(BaseAuthenticationIntrospector):
    """
    Introspector for BasicAuthentication class
    """
    name = 'basic_authentication'

    @property
    def security(self):
        security = super(BasicAuthenticationIntrospector, self).security
        security.extend([
            OrderedDict([(self.name, [])]),
        ])
        return security

    @property
    def security_definitions(self):
        """
        Collects authentication security definitions

        :return: authentication security definitions
        :rtype: dict
        """
        security_definitions = super(BasicAuthenticationIntrospector, self).security_definitions
        security_definitions.update(OrderedDict({
            self.name: {
                'type': 'basic',
                'description': """Clients should authenticate by passing the base64 encoded username:password string
                in the "Authorization HTTP header, prepended with the string "Basic ".
                For example:
                    Authorization: Basic dXNlcjpwYXNzd29yZA=="""
            }
        }))
        return security_definitions


class TokenAuthenticationIntrospector(BaseAuthenticationIntrospector):
    """
    Introspector for TokenAuthentication class
    """
    name = 'djangorestframework_token_authentication'

    @property
    def security(self):
        security = super(TokenAuthenticationIntrospector, self).security
        security.extend([
            OrderedDict({self.name: []})
        ])
        return security

    @property
    def security_definitions(self):
        """
        Collects authentication security definitions

        :return: authentication security definitions
        :rtype: dict
        """
        security_definitions = super(TokenAuthenticationIntrospector, self).security_definitions
        security_definitions.update(OrderedDict({
            self.name: {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': """Clients should authenticate by passing the token key in the "Authorization"
                HTTP header, prepended with the string "Token ".  For example:
                Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a"""
            }
        }))
        return security_definitions


def get_authentication_introspectors(view):
    """
    Get View Authentication Introspectors

    :param view: DjangoRestFramework View
    :return: list of authentication introspectors
    :rtype: list
    """
    from rest_framework import authentication
    authenticators_map = {
        authentication.BasicAuthentication: BasicAuthenticationIntrospector,
        authentication.TokenAuthentication: TokenAuthenticationIntrospector,
    }
    authenticators = getattr(view, 'authentication_classes', [])
    introspectors = []

    for authenticator in authenticators:
        introspectors.append(
            authenticators_map.get(authenticator, BaseAuthenticationIntrospector)(authenticator)
        )
    return introspectors
