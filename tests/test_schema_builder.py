import os
import json
import copy
from unittest import TestCase

from py2swagger import schema_builder


class SchemaBuilderTestCase(TestCase):

    def setUp(self):
        self.data = {
            'a': ['b', 'c'],
            'c': {
                'd': 'e',
            },
            'items': {
                'schema': {
                    'id': 'SchemaId'
                }
            }
        }

    def test_get_list_defs(self):
        self.assertEqual(['b', 'c'], schema_builder._get_list_defs(self.data, 'a'))
        self.assertEqual([], schema_builder._get_list_defs(self.data, 'x'))
        self.assertRaises(AttributeError, schema_builder._get_list_defs, 'data', 'a')

    def test_get_dict_values_defs(self):
        self.assertIn('e', schema_builder._get_dict_values_defs(self.data, 'c'))
        self.assertEqual([], list(schema_builder._get_dict_values_defs(self.data, 'x')))
        self.assertRaises(AttributeError, schema_builder._get_dict_values_defs, 'data', 'a')

    def test_get_array_defs(self):
        self.assertEqual([self.data['items']], schema_builder._get_array_defs(self.data))
        self.assertEqual([], schema_builder._get_array_defs({}))
        self.assertRaises(AttributeError, schema_builder._get_dict_values_defs, 'data', 'a')

    def test_get_global_defs(self):
        definitions = {
            'name1': {
                'k': 'v',
            },
            'name2': {
                'k': 'v',
            }
        }

        data = copy.deepcopy(definitions)
        result = schema_builder._get_global_defs(data)
        self.assertEqual(2, len(result))
        self.assertIn({'schema': {'k': 'v', 'id': 'name1'}}, result)
        self.assertEqual([], schema_builder._get_global_defs({}))
        self.assertRaises(TypeError, schema_builder._get_global_defs, {'k': 'v'})

    def test_extract_definitions(self):
        data = [
            {
                'schema': {
                    'id': 'TopSchema2',
                    'type': 'object',
                    'properties': {
                        'propname': {
                            'schema': {
                                'type': 'object',
                                'id': 'PropSchema'
                            }
                        }
                    }
                },
            },
            {
                'schema': {
                    'id': 'TopSchema1',
                    'type': 'array',
                    'items': {
                        'schema': {
                            'type': 'object',
                            'id': 'ArraySchema'
                        }
                    }
                },
            }

        ]

        self.assertEqual([], schema_builder._extract_definitions([]))
        self.assertEqual([], schema_builder._extract_definitions([{}]))
        self.assertEqual([], schema_builder._extract_definitions([{'k': 'v'}]))
        self.assertEqual([], schema_builder._extract_definitions([{'k': {}}]))

        result = schema_builder._extract_definitions(copy.deepcopy(data))

        self.assertEqual(4, len(result))
        self.assertIn({'type': 'object', 'id': 'ArraySchema'}, result)
        self.assertIn({'type': 'object', 'id': 'PropSchema'}, result)

    def test_schema_builder(self):
        config = {
            'version': '42',
            'title': 'Custom title',
            'description': 'Custom description',
            'host': 'host.name',
            'produces': ['feel/goodness'],
            'consumes': ['some/all'],
        }

        datamap_path = os.path.join(os.path.dirname(__file__), 'datamap.json')
        definitions_path = os.path.join(os.path.dirname(__file__), 'definitions.json')

        with open(datamap_path) as datamap_file:
            datamap = json.load(datamap_file)

        with open(definitions_path) as definitions_file:
            definitions = json.load(definitions_file)

        builder = schema_builder.SchemaBuilder(datamap, definitions=definitions, **config)

        result = builder.schema

        self.assertEqual(config['version'], result['info']['version'])
        self.assertEqual(config['title'], result['info']['title'])
        self.assertEqual(config['description'], result['info']['description'])

        self.assertEqual(config['host'], result['host'])
        self.assertEqual(config['produces'], result['produces'])
        self.assertEqual(config['consumes'], result['consumes'])

        self.assertEqual(1, len(result['paths']))
        self.assertIn(datamap[0][0], result['paths'])
        self.assertIn(datamap[0][1], result['paths'][datamap[0][0]])

        operation = result['paths'][datamap[0][0]][datamap[0][1]]

        self.assertNotIn('invalid_operation_parameter', operation)

        self.assertEqual(2, len(result['definitions']))

        self.assertIn('ResponseSerializer', result['definitions'])
        self.assertIn('FavoritesSerializer', result['definitions'])








