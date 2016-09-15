from abc import ABCMeta
from py2swagger.introspector import BaseDocstringIntrospector
from py2swagger.utils import OrderedDict


class BasePaginationIntrospector(BaseDocstringIntrospector):
    __metaclass__ = ABCMeta
    results_field = None
    response_fields = None

    def __init__(self, view=None, instance=None, si=None):
        """
        :param view: DjangoRestFramework view
        :param instance: DjangoRestFramework pagination class
        :param si: SerializerIntrospector
        """
        self.view = view
        self.si = si
        super(BasePaginationIntrospector, self).__init__(instance)

    @property
    def responses(self):
        """
        Create pagination responses
        :return: Reponses object
        :rtype: OrderedDict
        """
        responses = super(BasePaginationIntrospector, self).responses
        if self.si:
            if self.response_fields:
                response = OrderedDict([
                    ('description', 'Pagination response'),
                    ('schema', OrderedDict([
                        ('type', 'object'),
                        ('id', '{}Paginator'.format(self.si.name)),
                        ('required', []),
                        ('properties', OrderedDict())
                    ])),
                ])

                for field, field_type in self.response_fields:
                    response['schema']['required'].append(field)
                    if field == self.results_field:
                        response['schema']['properties'][field] = self.si.build_response_object(multiple=True)
                    else:
                        response['schema']['properties'][field] = OrderedDict(type=field_type)
                responses[200] = response

            else:
                responses[200] = OrderedDict([
                    ('description', 'Default response'),
                    ('schema', self.si.build_response_object(multiple=True)),
                ])

        return responses


class PageNumberPaginationIntrospector(BasePaginationIntrospector):
    """
    Introspector for DjangoRestFramework PageNumberPagination class
    """

    results_field = 'results'
    response_fields = (
        ('count', 'integer'),
        ('next', 'string'),
        ('previous', 'string'),
        (results_field, None),
    )

    @property
    def parameters(self):
        """
        Collects pagination parameters from pagination class
        :return: Parameters array
        :rtype: list
        """
        parameters = super(PageNumberPaginationIntrospector, self).parameters

        page_query_param = getattr(self._instance, 'page_query_param', None)
        if page_query_param:
            parameters.append(OrderedDict([
                ('in', 'query'),
                ('name', page_query_param),
                ('type', 'string'),
                ('description', 'Page parameter'),
                ('required', False),
            ]))

        return parameters


class LimitOffsetPaginationIntrospector(BasePaginationIntrospector):
    """
    Introspector for DjangoRestFramework LimitOffsetPagination class
    """
    results_field = 'results'
    response_fields = (
        ('count', 'integer'),
        ('next', 'string'),
        ('previous', 'string'),
        (results_field, None),
    )

    @property
    def parameters(self):
        """
        Collects pagination parameters from pagination class
        :return: Parameters array
        :rtype: list
        """
        parameters = super(LimitOffsetPaginationIntrospector, self).parameters

        limit_query_param = getattr(self._instance, 'limit_query_param', None)
        offset_query_param = getattr(self._instance, 'offset_query_param', None)
        default_limit = getattr(self._instance, 'default_limit', None)

        if limit_query_param:
            parameters.append(OrderedDict([
                ('in', 'query'),
                ('name', limit_query_param),
                ('type', 'string'),
                ('description', 'Limit parameter (default={})'.format(default_limit)),
                ('required', False),
            ]))

        if offset_query_param:
            parameters.append(OrderedDict([
                ('in', 'query'),
                ('name', offset_query_param),
                ('type', 'integer'),
                ('description', 'Offset parameter'),
                ('required', False),
            ]))
        return parameters


class CursorPaginationIntrospector(BasePaginationIntrospector):
    """
    Introspector for DjangoRestFramework CursorPagination class
    """
    results_field = 'results'
    response_fields = (
        ('next', 'string'),
        ('previous', 'string'),
        (results_field, None),
    )

    @property
    def parameters(self):
        """
        Collects pagination parameters from pagination class
        :return: Parameters array
        :rtype: list
        """
        parameters = super(CursorPaginationIntrospector, self).parameters

        cursor_query_param = getattr(self._instance, 'cursor_query_param', None)

        if cursor_query_param:
            parameters.append(OrderedDict([
                ('in', 'query'),
                ('name', cursor_query_param),
                ('type', 'string'),
                ('description', 'Cursor parameter'),
                ('required', False),
            ]))

        return parameters


class PaginationBySerializerIntrospector(BasePaginationIntrospector):
    """
    Introspector for DjangoRestFramework 2.0 pagination serializer
    """
    results_field = 'results'
    response_fields = (
        ('count', 'integer'),
        ('next', 'string'),
        ('previous', 'string'),
        (results_field, None),
    )

    @property
    def parameters(self):
        """
        Collects pagination parameters from view
        :return: Parameters array
        :rtype: list
        """
        parameters = super(PaginationBySerializerIntrospector, self).parameters

        page_kwarg = getattr(self.view, 'page_kwarg', None)
        paginate_by_param = getattr(self.view, 'paginate_by_param', None)
        paginate_by = getattr(self.view, 'paginate_by', None)

        if page_kwarg:
            parameters.append(OrderedDict([
                ('in', 'query'),
                ('name', page_kwarg),
                ('type', 'integer'),
                ('description', 'Page parameter'),
                ('required', False),
            ]))

        if paginate_by_param:
            parameters.append(OrderedDict([
                ('in', 'query'),
                ('name', self.view.paginate_by_param),
                ('type', 'integer'),
                ('description', 'Page size parameter (default={})'.format(paginate_by)),
                ('required', False),
            ]))

        return parameters


def get_pagination_introspector(view, si=None):
    """
    Create pagination introspector based on view
    :param view: DjangoRestFramework view
    :param si: SerializerIntrospector
    :return: PaginationIntrospector
    :rtype: BasePaginationIntrospector
    """
    if getattr(view, 'pagination_class', None):
        # DjangoRestFramework 3.0 pagination style with pagination class
        pagination_class = view.pagination_class
        from rest_framework import pagination
        if pagination_class == pagination.PageNumberPagination:
            return PageNumberPaginationIntrospector(view, pagination_class, si=si)
        elif pagination_class == pagination.LimitOffsetPagination:
            return LimitOffsetPaginationIntrospector(view, pagination_class, si=si)
        elif pagination_class == pagination.CursorPagination:
            return CursorPaginationIntrospector(view, pagination_class, si=si)
        else:
            return BasePaginationIntrospector(view, pagination_class, si=si)
    elif getattr(view, 'paginate_by', None):
        # DjangoRestFramework 2.0 pagination style with pagination serializer
        return PaginationBySerializerIntrospector(view=view, si=si)
    else:
        # Unrecognized view type
        return BasePaginationIntrospector(si=si)
