from rest_framework.viewsets import GenericViewSet, mixins

from .serializers import ModelSerializer

from django.conf import settings

if settings.REST_FRAMEWORK_V3:
    from rest_framework.pagination import LimitOffsetPagination, \
        PageNumberPagination, CursorPagination


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

else:
    from rest_framework.pagination import PaginationSerializer

    class TestPaginationSerializerViewSet(GenericViewSet, mixins.ListModelMixin):
        serializer_class = PaginationSerializer
        paginate_by = 1
