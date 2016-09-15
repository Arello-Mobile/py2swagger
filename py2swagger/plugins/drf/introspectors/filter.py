import inspect

from py2swagger.introspector import BaseDocstringIntrospector
from py2swagger.utils import OrderedDict


class BaseFilterBackendIntrospector(BaseDocstringIntrospector):
    """
    Found filter specific parameters and responses
    """

    def __init__(self, view, filter_backend):
        """
        :param view: DjangoRestFramework view instance
        :param filter_backend: filter backend class
        """
        self.view = view
        super(BaseFilterBackendIntrospector, self).__init__(filter_backend)


class DjangoFilterBackendIntrospector(BaseFilterBackendIntrospector):

    @property
    def parameters(self):
        parameters = super(DjangoFilterBackendIntrospector, self).parameters

        filter_fields = getattr(self.view, 'filter_fields', [])
        for field_name in filter_fields:
            parameters.append(OrderedDict({
                'in': 'query',
                'name': field_name,
                'type': 'string',
                'required': False,
                'description': 'Filter parameter'
            }))
        parameters.append(OrderedDict({
            'in': 'query',
            'name': 'o',
            'description': 'Ordering parameter',
            'type': 'string',
            'enum': list(filter_fields) + list(map(lambda f: '-{0}'.format(f), filter_fields))
        }))
        return parameters


class OrderingFilterBackendIntrospector(BaseFilterBackendIntrospector):

    @property
    def parameters(self):
        parameters = super(OrderingFilterBackendIntrospector, self).parameters
        ordering_fields = getattr(self.view, 'ordering_fields', [])
        ordering_param = getattr(self._instance, 'ordering_param', 'ordering')

        parameters.append(OrderedDict({
            'in': 'query',
            'name': ordering_param,
            'type': 'string',
            'enum': ordering_fields
        }))

        return parameters


def get_filter_introspectors(view):

    from rest_framework import filters

    filters_map = {
        filters.DjangoFilterBackend: DjangoFilterBackendIntrospector,
        filters.OrderingFilter: OrderingFilterBackendIntrospector,
    }
    filter_backends = getattr(view, 'filter_backends', [])
    introspectors = []

    for backend in filter_backends:
        backend = backend if inspect.isclass(backend) else backend.__class__
        introspectors.append(
            filters_map.get(backend, BaseFilterBackendIntrospector)(view, backend)
        )

    return introspectors
