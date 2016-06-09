from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .serializers import TestModelSeriazlizer
from .models import TestModel


class BaseViewSet(ModelViewSet):
    """
    BaseViewSet Summary
    ---
    parameters:
    - in: query
      name: base_param
      type: string
      required: false
    """

    def get_queryset(self):
        queryset = super(BaseViewSet, self).get_queryset()
        return queryset


class CustomViewSet(BaseViewSet):
    """
    CustomViewSet Summary
    ---
    tags:
    - custom_view
    parameters:
    - in: header
      name: get_param
      type: integer
      methods:
      - retreive
    responses:
          200:
            description: Response Description
            schema:
              type: array
            properties:
              status:
                type: integer
              message:
                type: string
          403:
            description: Error Description
            schema:
              type: object
              properties:
                status:
                  type: integer
                message:
                  type: string
    """

    serializer_class = TestModelSeriazlizer
    paginate_by = 100

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method
        ---
        tags:
        - custom_destroy
        parameters:
        - in: query
          name: destroy_param
          type: string
        """
        return Response(dict({}))


class EmailApiView(APIView):
    """
    tags:
    - send_email
    parameters:
    - in: formData
      name: id
      description: Person ID
      type: integer
      required: true
      methods:
      - post
    - in: formData
      name: email
      description: E-mail to send
      type: string
      required: true
      methods:
      - post
    responses:
      200:
        description: Status [200, 400, 403, 405]
        schema:
          type: object
          properties:
            status:
              type: integer
              enum: [200, 400, 403, 405]
    """

    def post(self, request):
        return Response(dict())


@api_view(['POST'])
def decorator_view(request):
    """
    tags:
    - test
    parameters:
    - in: formData
      name: id
      description: Person ID
      type: integer
      required: true
      methods:
      - post
    responses:
      200:
        description: Status [200, 400, 403, 405]
        schema:
          type: object
          properties:
            status:
              type: integer
              enum: [200, 400, 403, 405]
    """
    return Response(dict())


class RedefineViewSet(ModelViewSet):
    model = TestModel
    serializer_class = TestModelSeriazlizer

    def create(self, request, *args, **kwargs):
        """
        ---
        responses:
          201:
            description: 'Redefined response method'
            schema:
              allOf:
                - $ref: '#/definitions/TestModelSeriazlizer'
                - type: 'object'
                  properties:
                    new_custom_field1:
                      type: string
        """
        return Response(dict())

    def update(self, request, *args, **kwargs):
        """
        ---
        responses:
          201:
            description: 'Redefined response method'
            schema:
              allOf:
                - $ref: '#/definitions/TestModelSeriazlizer'
                - type: 'object'
                  properties:
                    new_custom_field2:
                      type: string
          200:
            description: 'Redefined response method'
            schema:
              allOf:
                - $ref: '#/definitions/TestModelSeriazlizer'
                - type: 'object'
                  properties:
                    new_custom_field3:
                      type: string
        """
        return Response(dict())

