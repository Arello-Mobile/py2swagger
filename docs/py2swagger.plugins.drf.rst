Django Rest Framework plugin for py2swagger
===========================================

What is this?
-------------

Makes (`swagger`_) specification for API (`Django REST framework`_) applications

.. _Django REST framework: http://www.django-rest-framework.org/
.. _swagger: http://swagger.io/


Launch
------

.. code-block:: bash

    py2swagger drf2swagger DJANGO_SETTINGS_MODULE


Parameters
----------

.. code-block:: bash

    usage: py2swagger drf2swagger [-h] django_settings

    positional arguments:
        django_settings       Path to django settings module


Features
--------

- Pagination support
- Filter support
- Authentication classes support
- Serializers support
- Support parameters help_text, default, max_length, min_length, choices in serializers and models
- YAML-documentation support in classes, methods, decorators, custom filters, custom authorization classes


YAML Docstring
--------------

Example:

.. code-block:: python

    @api_view(["POST"])
    def view(request):
        """
        Method summary
        Method description
        may be more than
        one line
        ---
        tags:
        - method_tags
        serializers:
          request:
            path: project.module.serializers.SomeSerializer
          response:
            path: project.module.serializers.AnotherSerializer
        parameters:
        - in: query
          name: param
          description: Parameter Description
          type: integer
          required: true
          default: 0
        - in: body
          name: data
          schema:
            type: object
            id: SomeSerializer
        responses:
          200:
            description: Response Description
            schema:
              type: array
              items:
                type: object
                id: AnotherSerializer
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
        ...


**YAML Docstring Priority**

method -> decorator -> class -> parent class


Examples
++++++++


Authorization:

.. code-block:: python

    class CustomAuthentication(authentication.BaseAuthentication):
        """
        ---
        security:
          api_key: []
        parameters:
          - in: header
            type: apiKey
            name: Auth-Token
            description: Some Header Description
        """
        ...

Serializer:

.. code-block:: python

    class PointImageSerializer(serializers.ModelSerializer):
        """
        ---
        fields:
          custom_field:
            response:
              schema:
                type: object
                id: SomeField
                required:
                - original
                - preview
                properties:
                  original:
                    type: string
                  preview:
                    type: string
          another_field:
            required: false
            readOnly: true
            type: string
            format: email
            description: Field description
          array_field:
            required: false
            request:
              type: string
              default: "a, b, c"
              description: Field description
            response:
              required: true
              type: array
              description: Field description
              items:
                type: string
        """
        ...

Method:

.. code-block:: python

    class SomeViewSet(viewsets.ReadOnlyModelViewSet):
        """
        ---
        tags:
        - some_tag
        parameters:
        - in: query
          name: param1
          description: Param Description
          type: integer
          required: false
          methods:
          - list
        """
        permission_classes = (IsAuthenticated, )
        queryset = Exhibition.objects.all()
        serializer_class = ExhibitionSerializer

        def get(self):
            """
            Method summary
            """
            ...

        ...

If list option **methods** exists in parameter, this parameter add only to methods in option value,
else parameter add to all methods
