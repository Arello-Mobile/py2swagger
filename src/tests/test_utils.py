from django.test import TestCase

from py2swagger.utils import get_decorators


def not_decorated_function():
    pass


def my_decorator(func):
    def wrapper(*args, **kwargs):
        """
        Decorator Docstring
        """
        result = func(*args, **kwargs)
        return result * result
    return wrapper


@my_decorator
def decorated_function(n):
    """
    Decorated Function Docstring
    """
    return n


class GetDecoratorsTestCase(TestCase):
    def test_with_decorator(self):
        decorators = get_decorators(decorated_function)

        self.assertEqual(2, len(decorators))
        self.assertIn(decorated_function, decorators)

    def test_without_decorator(self):
        decorators = get_decorators(not_decorated_function)

        self.assertEqual(1, len(decorators))
        self.assertIn(not_decorated_function, decorators)
