from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView


class TestBasicAuthView(APIView):
    authentication_classes = (BasicAuthentication, )


class TestTokenAuthView(APIView):
    authentication_classes = (TokenAuthentication, )


class TestGetAuthIntrospectorsView(APIView):
    authentication_classes = (BasicAuthentication, TokenAuthentication,)
