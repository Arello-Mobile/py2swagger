from abc import ABCMeta, abstractmethod
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from .method import BaseMethodIntrospector, ViewSetMethodIntrospector, ApiViewMethodIntrospector, \
    WrappedApiViewMethodIntrospector

from ..exceptions import IntrospectorException
from py2swagger.introspector import BaseDocstringIntrospector


class BaseViewIntrospector(BaseDocstringIntrospector):
    """
    Base DjangoRestFramework view introspector
    """
    __metaclass__ = ABCMeta

    method_introspector = BaseMethodIntrospector

    def __init__(self, path, callback, pattern):
        self.path = path
        self.callback = callback
        self.pattern = pattern

        super(BaseViewIntrospector, self).__init__(callback)

    def __iter__(self):
        """
        Iterates through view methods
        """
        for method in self.methods():
            yield method

    @abstractmethod
    def methods(self):
        """
        Finds view methods
        :return: Iterable object
        """
        raise NotImplementedError('Not implemented yet')


class ViewSetIntrospector(BaseViewIntrospector):
    """
    Introspector for DjangoRestFramework ViewSet views
    """

    method_introspector = ViewSetMethodIntrospector

    def methods(self):
        """
        :return: Iterable object
        """
        # ViewSet view handler
        # TODO: describe why we using "actions" property. See injection.py
        methods = self.pattern.callback.actions
        return map(lambda m: self.method_introspector(self, *m), methods.items())


class ApiViewIntrospector(BaseViewIntrospector):
    """
    Introspector for DjangoRestFramework ApiView views
    """
    method_introspector = ApiViewMethodIntrospector

    def methods(self):
        """
        :return: Iterable object
        """
        methods = self.callback().allowed_methods
        return map(lambda x: self.method_introspector(self, x), methods)


class WrappedApiViewIntrospector(ApiViewIntrospector):
    """
    Introspector for DjangoRestFramework decorated views
    """
    method_introspector = WrappedApiViewMethodIntrospector


def get_view_introspector(api):
    """
    Creates view introspector based on api

    :param api:
    :rtype: BaseViewIntrospector
    """
    callback = api['callback']

    def inmodule(callback, module_name):
        return callback.__module__ == module_name

    map = (
        (issubclass, ViewSetMixin, ViewSetIntrospector),
        (inmodule, 'rest_framework.decorators', WrappedApiViewIntrospector),
        (issubclass, APIView, ApiViewIntrospector),
    )

    for f, param, introspector_class in map:
        if f(callback, param):
            return introspector_class(**api)

    raise IntrospectorException('View introspector not recognized')
