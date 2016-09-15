from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.views import APIView


class TestDjangoFilterBackendView(APIView):
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('test_filter_field_1', 'test_filter_field_2',)


class TestOrderingFilterView(APIView):
    filter_backends = (OrderingFilter, )
    ordering_fields = ('test_filter_field_1', 'test_filter_field_2',)


class TestGetFilterIntrospectorsView(APIView):
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
