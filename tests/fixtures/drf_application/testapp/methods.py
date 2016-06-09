from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.filters import DjangoFilterBackend

from django.conf import settings

from .serializers import IncludedSerializer


class TestAPIView(APIView):

    def get(self, request):
        """
        TestAPIView GET Summary
        Test Description
        ---
        tags:
        - custom_view
        """
        pass

    def post(self):
        """
        ---
        serializers:
          request:
            path: testapp.serializers.IncludedSerializer
          response:
            path: testapp.serializers.IncludedSerializer
        """
        pass

    def destroy(self):
        """
        ---
        responses:
          200:
            description: OK
        """
        pass


class BaseTestViewSet(GenericViewSet, mixins.ListModelMixin):
    """
    ---
    serializers:
      response:
        path: testapp.serializers.IncludedSerializer
    """
    serializer_class = IncludedSerializer
    filter_backends = (DjangoFilterBackend, )


if settings.REST_FRAMEWORK_V3:
    from rest_framework.pagination import LimitOffsetPagination

    class TestViewSet(BaseTestViewSet):
        pagination_class = LimitOffsetPagination
else:
    from rest_framework.pagination import PaginationSerializer

    class TestViewSet(BaseTestViewSet):
        serializer_class = PaginationSerializer

