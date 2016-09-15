from unittest import TestCase
from py2swagger import utils


# from py2swagger.utils import get_decorators


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


class A(object):
    pass


class B(object):
    pass


class C(A):
    pass


class D(B):
    pass


class E(C, D):
    pass


class Py2SwaggerUtilsTestCase(TestCase):
    def test_get_decorator_decorated(self):
        decorators = utils.get_decorators(decorated_function)
        self.assertEqual(2, len(decorators))
        self.assertIn(decorated_function, decorators)

    def test_get_decorator_not_decorated(self):
        decorators = utils.get_decorators(not_decorated_function)

        self.assertEqual(1, len(decorators))
        self.assertIn(not_decorated_function, decorators)

    def test_yaml_loader_mixin(self):
        valid_yaml_data = """---
        arr:
        - 1
        - 2
        - 3
        dict:
         key: value
        """

        invalid_yaml_data = """---
        block:
        - not:
          valid
           indent
        """

        valid_result = utils.YAMLLoaderMixin.yaml_load(valid_yaml_data)

        self.assertTrue(isinstance(valid_result, utils.OrderedDict))
        self.assertIn('arr', valid_result)
        self.assertIn('dict', valid_result)

        invalid_result = utils.YAMLLoaderMixin.yaml_load(invalid_yaml_data)
        self.assertIsNone(invalid_result)

        empty_result = utils.YAMLLoaderMixin.yaml_load(None)
        self.assertIsNone(empty_result)

    def test_flatten(self):
        data = [
            (1, 2, 3),
            [4, (5, 6)],
            [7, 8],
            9
        ]
        expected = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        result = utils.flatten(data)

        self.assertListEqual(expected, result)

    def test_mro_list(self):

        self.assertEqual(1, len(utils.get_mro_list(A)))

        self.assertEqual(1, len(utils.get_mro_list(B)))

        c_mro = utils.get_mro_list(C)
        self.assertEqual(2, len(c_mro))
        self.assertIn(A, c_mro)

        d_mro = utils.get_mro_list(D)
        self.assertEqual(2, len(d_mro))
        self.assertIn(B, d_mro)

        e_mro = utils.get_mro_list(E)
        self.assertEqual(5, len(e_mro))
        self.assertIn(A, e_mro)
        self.assertIn(B, e_mro)
        self.assertIn(C, e_mro)
        self.assertIn(D, e_mro)

    def test_extract_class_path(self):

        simple_path = 'ClassName'

        s_module_path, s_class_name = utils._extract_class_path(simple_path)

        self.assertIsNone(s_module_path)
        self.assertEqual(s_class_name, simple_path)

        advanced_path = 'some.module.ModuleClassName'
        a_module_path, a_class_name = utils._extract_class_path(advanced_path)

        self.assertEqual(a_class_name, 'ModuleClassName')
        self.assertEqual(a_module_path, 'some.module')

    def test_load_class(self):

        absolute_path = 'py2swagger.utils.YAMLLoaderMixin'
        result = utils.load_class(absolute_path)
        self.assertEqual(result, utils.YAMLLoaderMixin)

        relative_path = '.py2swagger.utils.YAMLLoaderMixin'
        class_only = 'YAMLLoaderMixin'
        invalid_class_name = 'py2swagger.utils.SomeNotExistingClass'
        invalid_module_path = 'somelib.utils.SomeNotExistingClass'

        self.assertRaises(ImportError, utils.load_class, relative_path)
        self.assertRaises(ImportError, utils.load_class, class_only)
        self.assertRaises(ImportError, utils.load_class, invalid_class_name)
        self.assertRaises(ImportError, utils.load_class, invalid_module_path)

    def test_clean_parameters(self):

        test_parameters_raw = """---
        - name: p1
          in: query
          type: string
          methods:
          - all
        - name: p1
          in: query
          type: integer
          methods:
          - all
        - name: p2
          in: body
          type: string
        - name: p3
          in: header
          type: integer
          methods:
          - get
        - name: p4
          in: header
          type: integer
          methods:
          - get
          - post
        - name: p5
          in: formData
          type: integer
        - name: p6
          in: formData
          type: string
        """

        file_parameters_raw = """---
        - name: p7
          in: formData
          type: file
        """

        test_parameters = utils.YAMLLoaderMixin.yaml_load(test_parameters_raw)
        file_parameters = utils.YAMLLoaderMixin.yaml_load(file_parameters_raw)

        result = utils.clean_parameters(test_parameters, method='get')

        self.assertEqual(4, len(result))

        result = utils.clean_parameters(test_parameters, method='post')

        self.assertEqual(3, len(result))

        merged_parameters = test_parameters + file_parameters
        result = utils.clean_parameters(merged_parameters, method='get')

        self.assertEqual(6, len(result))

    def test_yaml_ordered_dict(self):

        data = """---
        a: 1
        b: 2
        c: 3
        """

        result = utils.yaml.load(data)

        self.assertTrue(isinstance(result, utils.OrderedDict))
        self.assertEqual(['a', 'b', 'c'], list(result.keys()))

        result = utils.yaml.dump(result)

        index_a = result.index('a')
        index_b = result.index('b')
        index_c = result.index('c')
        self.assertTrue(index_a < index_b < index_c)

    def test_update_settings(self):
        config = {
            'version': '42',
            'title': 'Custom title',
            'description': 'Custom description',
            'host': 'host.name',
            'produces': ['feel/goodness'],
            'consumes': ['some/all'],
            'definitions': {}
        }
        extend_config = {
            'version': 23,
            'definitions': {
                'a': {
                    'type': 'integer'
                }
            },
            'consumes': ['text/plain'],
        }
        expected_result = {
            'description': 'Custom description',
            'produces': ['feel/goodness'],
            'title': 'Custom title',
            'host': 'host.name',
            'version': 23,
            'definitions': {'a': {'type': 'integer'}},
            'consumes': ['some/all', 'text/plain']
        }
        self.assertDictContainsSubset(expected_result, utils.update_settings(config, extend_config))


