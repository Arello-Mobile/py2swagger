from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.pagination import LimitOffsetPagination, \
    PageNumberPagination, CursorPagination
from .serializers import ModelSerializer

class TestLimitOffsetPaginationViewSet(GenericViewSet, mixins.ListModelMixin):
    """
    ---
    serializers:
      response:
        path: testapp.serializers.IncludedSerializer
    """
    serializer_class = ModelSerializer
    pagination_class = LimitOffsetPagination


class TestPageNumberPaginationViewSet(GenericViewSet, mixins.ListModelMixin):
    serializer_class = ModelSerializer
    pagination_class = PageNumberPagination


class TestCursorPaginationViewSet(GenericViewSet, mixins.ListModelMixin):
    serializer_class = ModelSerializer
    pagination_class = CursorPagination
