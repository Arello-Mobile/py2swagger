from abc import ABCMeta
import re

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from py2swagger.introspector import BaseDocstringIntrospector
from py2swagger.utils import get_decorators, OrderedDict, load_class, clean_parameters, flatten
from rest_framework.views import get_view_name
from rest_framework import status

from .authentication import get_authentication_introspectors
from .filter import get_filter_introspectors
from .pagination import get_pagination_introspector
from .serializer import SerializerIntrospector


class BaseMethodIntrospector(BaseDocstringIntrospector):
    """
    Base DjangoRestFramework method introspector
    """
    __metaclass__ = ABCMeta

    DEFAULT_STATUS_CODE = status.HTTP_200_OK
    STATUS_CODES = {
        'create': status.HTTP_201_CREATED,
        'destroy': status.HTTP_204_NO_CONTENT
    }

    def __init__(self, view_introspector, http_method, method=None):
        self.http_method = http_method.upper()
        self.method = method or self.http_method.lower()
        self.introspector = view_introspector
        self.callback = view_introspector.callback
        self.method_callback = self._method_callback()
        self.view = self._create_view()

        super(BaseMethodIntrospector, self).__init__(self.method_callback)

        self.auth_introspectors = get_authentication_introspectors(self.view)

    def _create_view(self):
        """
        Creates DjangoRestFramework view
        :return: view
        """
        view = self.callback()

        view.kwargs = getattr(view, 'kwargs', dict())
        if hasattr(self.introspector.pattern, 'default_args'):
            view.kwargs.update(self.introspector.pattern.default_args)

        view.request = HttpRequest()
        view.request.user = AnonymousUser()
        view.request.method = self.method

        return view

    def _method_callback(self):
        """
        Creates callback from method
        :return: method callback
        """
        return getattr(self.callback, self.method, None)

    def _get_tags(self):
        """
        Get swagger operation tags for method
        Always returns at least one tag

        :return: swagger tags
        :rtype: list
        """
        tags = self.parser.get_tags() or self.introspector.parser.get_tags()
        if not tags:
            tags = [get_view_name(self.introspector.callback).lower()]

        return tags

    def _get_summary(self):
        """
        Get swagger operation summary for method
        Always returns value

        :return: swagger summary
        :rtype: str
        """
        summary = self.parser.get_summary()

        if not summary:
            summary = '{method} {view_name}'.format(
                method=self.method,
                view_name=get_view_name(self.introspector.callback)
            ).replace('_', ' ').title()

        return summary

    def _get_consumes(self):
        """
        Get method consumes contenttypes

        :rtype: list
        """
        consumes = [getattr(parser, 'media_type') for parser in self.view.parser_classes if
                    hasattr(parser, 'media_type')]
        return consumes

    def _get_produces(self):
        """
        Get method produces contenttypes

        :rtype: list
        """
        produces = [getattr(renderer, 'media_type') for renderer in self.view.renderer_classes if
                    hasattr(renderer, 'media_type')]
        return produces

    def _get_description(self):
        """
        Get method description from docstring

        :rtype: str
        """
        return self.parser.get_description()

    @property
    def parameters(self):
        """
        Collects parameters from introspectors

        :return: list of parameters
        :rtype: list
        """
        parameters = super(BaseMethodIntrospector, self).parameters
        parameters.extend(self.introspector.parameters)

        # add serializer parameters only in several http methods
        if self.http_method.lower() in ('post', 'put', 'patch'):
            serializer = self._get_serializer(request=True)
            if serializer:
                si = SerializerIntrospector(serializer)
                parameters.extend(si.get_parameters())

        # add filter and pagination parameters only in 'list' methods
        if 'list' in self.method.lower():
            # filter parameters
            filter_introspectors = get_filter_introspectors(self.view)
            for filter_introspector in filter_introspectors:
                parameters.extend(filter_introspector.parameters)
            # pagination parameters
            pagination_introspector = get_pagination_introspector(self.view)
            parameters.extend(pagination_introspector.parameters)

        # path parameters
        parameters.extend(self._get_path_parameters())

        return parameters

    def _get_path_parameters(self):
        """
        Creates parameters described in url path
        :return: list of parameters
        :rtype: list
        """
        params = []
        url_parameters = re.findall(r'/{(.+?)}', self.introspector.path)

        for parameter in url_parameters:
            params.append({
                'name': parameter,
                'type': 'string',
                'in': 'path',
                'required': True
            })

        return params

    def _get_parameters(self):
        """
        Collects and clean method parameters

        :return: list of parameters
        :rtype: list
        """
        return clean_parameters(self.parameters, self.method)

    @property
    def responses(self):
        """
        Collects method responses

        :return: swagger responses object
        :rtype: OrderedDict
        """
        responses = OrderedDict()
        responses.update(self.introspector.responses)
        responses.update(super(BaseMethodIntrospector, self).responses)

        serializer = self._get_serializer()

        if serializer and not responses.get(200, None):
            si = SerializerIntrospector(serializer)
            if 'list' in self.method.lower():
                pagination_introspector = get_pagination_introspector(self.view, si=si)
                responses.update(pagination_introspector.responses)
            else:
                response = OrderedDict([
                    ('description', 'Default response'),
                    ('schema', si.build_response_object()['schema']),
                ])
                responses[200] = response

        status_code = self.STATUS_CODES.get(self.method, self.DEFAULT_STATUS_CODE)
        response = responses.pop(200, None)
        # TODO this code wants to be rewritten
        if response:
            if status_code == status.HTTP_204_NO_CONTENT:
                response.pop('schema', None)
            if not responses.get(status_code, None):
                responses[status_code] = response

        if status_code not in responses:
            response = OrderedDict([
                ('description', 'Empty response'),
            ])
            responses[status_code] = response

        return responses

    def _get_serializer(self, request=False):
        """
        Get serializer for method
        Try to find serializer in method docstring or load method serializer

        :param request: is request serializer?
        :return: DjangoRestFramework Serializer Class
        """
        for parser in flatten((self.parsers, self.introspector.parsers)):
            serializer_path = parser.get_serializer(request)
            if serializer_path:
                return load_class(serializer_path)
        return self._get_view_serializer()

    def _get_view_serializer(self):
        """
        Get method serializer

        :return: DjangoRestFramework Serializer Class
        """
        serializer = None
        if hasattr(self.callback, 'get_serializer_class'):
            view = self._create_view()
            if view is not None:
                serializer = view.get_serializer_class()
        return serializer

    def get_serializers(self):
        """
        Get all serializers for method
        this method used for collect definitions

        :return: list DjangoRestFramework Serializer Class
        :rtype: list
        """
        serializers = []
        for parser in flatten((self.parsers, self.introspector.parsers)):
            serializer_paths = parser.get_serializers()
            for serializer_path in serializer_paths:
                serializers.append(load_class(serializer_path))

        serializer = self._get_view_serializer()
        if serializer:
            serializers.append(serializer)

        return serializers

    def get_security_definitions(self):
        security_definitions = super(BaseMethodIntrospector, self).security_definitions
        for introspector in flatten(self.auth_introspectors):
            security_definitions.update(introspector.security_definitions)
        return security_definitions

    def _get_security(self):
        security = super(BaseMethodIntrospector, self).security
        for introspector in flatten(self.auth_introspectors):
            security.extend(introspector.security)
        return security

    def get_operation(self):
        """
        Get full swagger operation object

        :return: swagger operation object
        :rtype: OrderedDict
        """

        operation = OrderedDict(
            tags=self._get_tags(),
            summary=self._get_summary(),
            description=self._get_description(),
            parameters=self._get_parameters(),
            produces=self._get_produces(),
            consumes=self._get_consumes(),
            responses=self.responses,
            security=self._get_security()
        )

        # TODO: SECURITY OBJECT SECURITY DEFINITIONS
        for key, value in list(operation.items()):
            # Remove empty keys
            if not value:
                operation.pop(key)

        return operation


class ViewSetMethodIntrospector(BaseMethodIntrospector):
    """
    Introspector for DjangoRestFramework ViewSet methods
    """

    def _create_view(self):
        view = super(ViewSetMethodIntrospector, self)._create_view()
        if not hasattr(view, 'action'):
            setattr(view, 'action', self.method)
        view.request.method = self.http_method
        return view


class ApiViewMethodIntrospector(BaseMethodIntrospector):
    """
    Introspector for DjangoRestFramework ApiView methods
    """
    def _method_callback(self):
        m = super(ApiViewMethodIntrospector, self)._method_callback()
        m = get_decorators(m)[-1]
        return m


class WrappedApiViewMethodIntrospector(BaseMethodIntrospector):
    """
    Introspector for DjangoRestFramework wrapped with decorators methods
    """
    def _method_callback(self):
        return self.callback
