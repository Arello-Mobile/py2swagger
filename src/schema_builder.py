import six

from .utils import OrderedDict


class SchemaBuilder(object):

    def __init__(self, datamap, **schema_properties):
        self._schema_paths = None
        self._schema_definitions = None
        self._schema = None
        self._kwargs = schema_properties

        self.datamap = datamap

    @property
    def schema(self):
        if not self._schema:
            self._generate_schema()
        return self._schema

    def _generate_schema(self):
        self._schema_paths = OrderedDict()
        self._schema_definitions = OrderedDict()

        self._schema = OrderedDict()
        self._schema['swagger'] = '2.0'
        self._schema['info'] = self._kwargs.get('info', {
            'version': self._kwargs.get('version', '0.0.1'),
            'title': self._kwargs.get('title', 'Service API'),
            'description': self._kwargs.get('description', ''),
        })
        self._schema['host'] = self._kwargs.get('host', 'localhost:8000')
        self._schema['basePath'] = self._kwargs.get('basePath', '/')
        self._schema['produces'] = self._kwargs.get('produces', ['application/json'])
        self._schema['consumes'] = self._kwargs.get('consumes', ['application/json'])
        self._schema['paths'] = self._schema_paths
        self._schema['definitions'] = self._schema_definitions

        schema_definitions = _extract_definitions(_get_global_defs(self._kwargs.get('definitions', {})))
        self._update_definitions(schema_definitions)

        for url, method, obj in self.datamap:
            parameters_definitions = _extract_definitions(_get_list_defs(obj, 'parameters'))
            responses_definitions = _extract_definitions(_get_dict_values_defs(obj, 'responses'))
            self._update_definitions(parameters_definitions + responses_definitions)
            self._update_path(url, method, self._get_operation(obj))

    def _update_definitions(self, defs):
        for definition in defs:
            def_id = definition.pop('id')
            if def_id is not None:
                if self._schema_definitions.get(def_id, None):
                    self._schema_definitions[def_id].update(definition)
                else:
                    self._schema_definitions[def_id] = definition

    def _get_operation(self, obj):
        operation = OrderedDict(
            summary=obj.get('summary', None),
        )

        optional_fields = [
            'tags',
            'consumes',
            'produces',
            'schemes',
            'security',
            'deprecated',
            'operationId',
            'externalDocs'
        ]
        for key in optional_fields:
            if key in obj:
                operation[key] = obj.get(key)

        if 'description' in obj:
            operation['description'] = obj['description']

        # parameters - swagger ui dislikes empty parameter lists
        if 'parameters' in obj:
            operation['parameters'] = obj['parameters']

        operation['responses'] = obj.get('responses', {})
        return operation

    def _update_path(self, url, method, operation):
        if url not in self._schema_paths:
            self._schema_paths[url] = OrderedDict()
        self._schema_paths[url][method] = operation


def _extract_definitions(data, l=0):
    """
    Since we couldn't be bothered to register models elsewhere
    our definitions need to be extracted from the parameters.
    We require an 'id' field for the schema to be correctly
    added to the definitions list.
    """

    definitions = []
    if not data:
        return definitions
    for item in data:
        if 'schema' in item and item['schema']:
            schema = item['schema']
            schema_id = schema.get('id')
            if schema_id:
                definitions.append(schema)
                ref = {'$ref': '#/definitions/{}'.format(schema_id)}

                if l > 0:
                    item.update(ref)
                    del item['schema']
                else:
                    item['schema'] = ref

            definitions += _extract_definitions(_get_dict_values_defs(schema, 'properties'), l + 1)
            definitions += _extract_definitions(_get_array_defs(schema), l + 1)
        definitions += _extract_definitions(_get_array_defs(item), l + 1)

    return definitions


def _get_list_defs(source, key):
    return source.get(key, [])


def _get_dict_values_defs(source, key):
    return source.get(key, {}).values()


def _get_array_defs(source):
    ret = []
    items = source.get('items')
    if items and 'schema' in items:
        return [items]
    return ret


def _get_global_defs(source):
    defs = []
    for d, v in six.iteritems(source):
        v['id'] = d
        defs.append({'schema': v})
    return defs
