from unittest import TestCase
from py2swagger.introspector import BaseDocstringIntrospector


class Parent(object):
    """
    Parent Class Docstring
    ---
    parameters:
    - name: parent_parameter
      type: string
    - name: overrided_parameter
      type: string
    responses:
        200:
            description: Parent 200 response
        401:
            description: Parent 401 response
    security:
    - parent_api_key: []
    securityDefinitions:
      parent_api_key:
        type: apiKey
        name: Auth-Token
        in: header
    """
    pass


class Child(Parent):
    """
    Child Class Docstring
    ---
    parameters:
    - name: child_parameter
      type: string
    - name: overrided_parameter
      type: integer
    responses:
      200:
        description: Child 200 response
      403:
        description: Child 403 response
    security:
    - child_api_key: []
    securityDefinitions:
      child_api_key:
        type: apiKey
        name: Auth-Token
        in: header
    """
    pass


def decorator(func):
    def wrapper(*args, **kwargs):
        """
        Decorator Docstring
        ---
        parameters:
        - name: decorator_parameter
          type: string
        - name: overrided_parameter
          type: string
        responses:
          200:
            description: Decorator 200 response
          401:
            description: Decorator 401 response
        security:
        - decorator_api_key: []
        securityDefinitions:
          decorator_api_key:
            type: apiKey
            name: Auth-Token
            in: header
        """
        result = func(*args, **kwargs)
        return result * result

    return wrapper


@decorator
def decorated_function(n):
    """
    Decorated Function Docstring
    ---
    parameters:
    - name: function_parameter
      type: string
    - name: overrided_parameter
      type: integer
    responses:
      200:
        description: Decorator 200 response
      403:
        description: Decorator 403 response
    security:
    - decorator_api_key: []
    securityDefinitions:
      decorator_api_key:
        type: apiKey
        name: Auth-Token
        in: header
    """
    return n


class BaseDocstringIntrospectorTestCase(TestCase):

    def test_parsers(self):
        introspector = BaseDocstringIntrospector(Child)

        self.assertEqual(3, len(introspector.parsers))
        self.assertIn(introspector.parser, introspector.parsers)

    def test_function_parser(self):

        f = decorator(lambda x: x)

        introspector = BaseDocstringIntrospector(f)

        parameters = introspector.parameters
        responses = introspector.responses
        security = introspector.security
        security_definitions = introspector.security_definitions
        parser = introspector.parser

        self.assertEqual(2, len(parameters))
        self.assertEqual(2, len(responses.keys()))
        self.assertEqual(1, len(security))
        self.assertEqual(2, len(security_definitions.keys()))

        self.assertEqual('Decorator Docstring', parser.get_summary())

    def test_class_parser(self):
        introspector = BaseDocstringIntrospector(Parent)

        parameters = introspector.parameters
        responses = introspector.responses
        security = introspector.security
        security_definitions = introspector.security_definitions
        parser = introspector.parser

        self.assertEqual(2, len(parameters))
        self.assertEqual(2, len(responses.keys()))
        self.assertEqual(1, len(security))
        self.assertEqual(2, len(security_definitions.keys()))

        self.assertEqual('Parent Class Docstring', parser.get_summary())

    def test_inherited_class_parser(self):
        introspector = BaseDocstringIntrospector(Child)

        parameters = introspector.parameters
        responses = introspector.responses
        security = introspector.security
        security_definitions = introspector.security_definitions
        parser = introspector.parser

        self.assertEqual(4, len(parameters))
        self.assertEqual(3, len(responses.keys()))
        self.assertEqual(2, len(security))
        self.assertEqual(3, len(security_definitions.keys()))

        self.assertEqual('Child Class Docstring', parser.get_summary())

    def test_decorated_function_parser(self):
        introspector = BaseDocstringIntrospector(decorated_function)

        parameters = introspector.parameters
        responses = introspector.responses
        security = introspector.security
        security_definitions = introspector.security_definitions
        parser = introspector.parser

        self.assertEqual(4, len(parameters))
        self.assertEqual(3, len(responses.keys()))
        self.assertEqual(2, len(security))
        self.assertEqual(3, len(security_definitions.keys()))

        self.assertEqual('Decorator Docstring', parser.get_summary())
