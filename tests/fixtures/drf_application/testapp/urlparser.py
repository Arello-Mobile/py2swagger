from django.views.generic import View
from rest_framework.views import APIView


class MockApiView(APIView):
    """
    A Test View
    This is more commenting
    """

    def get(self, request):
        """
        Get method specific comments
        """
        pass


class NonApiView(View):
    pass
