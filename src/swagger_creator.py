import inspect
import json
import os
import re
import six

from .utils import OrderedDict, YAMLLoaderMixin


class SwaggerCreator(YAMLLoaderMixin):

    def __init__(self, **kwargs):

        self.output = OrderedDict()
        self.output['swagger'] = '2.0'
        self.output['info'] = kwargs.get('info', {
            'version': kwargs.get('version', '0.0.1'),
            'title': kwargs.get('title', 'Service API'),
            'description': kwargs.get('description', ''),
        })

        self.output['host'] = kwargs.get('host', 'localhost:8000')
        self.output['basePath'] = kwargs.get('basePath', '/')

        self.output['produces'] = kwargs.get('produces', ['application/json'])
        self.output['consumes'] = kwargs.get('consumes', ['application/json'])

        definitions = kwargs.get('definitions', dict())

        self.definitions = OrderedDict()
        self.update_definitons(definitions)

        self.paths = OrderedDict()

        self.output['paths'] = self.paths
        self.output['definitions'] = self.definitions

    def update_definitons(self, definitions):
        defs = []
        for d, v in six.iteritems(definitions):
            v['id'] = d
            defs.append({'schema': v})
        defs = self._extract_definitions(defs)
        for definition in defs:
            def_id = definition.pop('id')
            if def_id is not None:
                if self.definitions.get(def_id, None):
                    self.definitions[def_id].update(definition)
                else:
                    self.definitions[def_id] = definition

    @classmethod
    def _load_data(cls, obj):
        if isinstance(obj, (six.string_types, six.text_type)):
            return cls._load_from_str(obj)
        elif isinstance(obj, dict):
            return cls._load_from_dict(obj)
        else:
            return cls._parse_docstring(obj)

    @classmethod
    def _load_from_str(cls, data):
        obj = cls.yaml_load(data)
        return cls._load_from_dict(obj)

    @staticmethod
    def _load_from_dict(obj):
        summary = obj.get('summary', None)
        description = obj.get('description', None)
        swag = obj
        return summary, description, swag

    @classmethod
    def _parse_docstring(cls, obj):

        docstring = cls._retreive_docstring(obj)

        summary, description, schema = None, None, None
        if '---' in docstring:
            head, yml = re.split(r'\s*---*\s*', docstring)
            if yml:
                schema = cls.yaml_load(yml)
        else:
            head = docstring

        if '\n' in head.strip():
            summary, description = head.split('\n', 1)
        else:
            summary = head.strip()

        return summary, description, schema

    @staticmethod
    def _retreive_docstring(obj):
        return inspect.getdoc(obj)

    def generate(self, datamap):

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

        for url, method, obj in datamap:

            operations = OrderedDict()

            summary, description, swag = self._load_data(obj)
            if swag is not None:
                params = swag.get('parameters', [])
                defs = self._extract_definitions(params)
                responses = swag.get('responses', {})
                if responses is not None:
                    defs = defs + self._extract_definitions(responses.values())

                for definition in defs:
                    def_id = definition.pop('id')
                    if def_id is not None:
                        if self.definitions.get(def_id, None):
                            self.definitions[def_id].update(definition)
                        else:
                            self.definitions[def_id] = definition

                operation = OrderedDict(
                    summary=summary,
                )
                # other optionals
                for key in optional_fields:
                    if key in swag:
                        operation[key] = swag.get(key)

                if description:
                    operation['description'] = description

                # parameters - swagger ui dislikes empty parameter lists
                if len(params) > 0:
                    operation['parameters'] = params

                operation['responses'] = responses
                operations[method] = operation
                if self.paths.get(url, None):
                    self.paths[url].update(operations)
                else:
                    self.paths[url] = operations

        return self.output

    @staticmethod
    def _sanitize(comment):
        return comment.replace('\n', '<br/>') if comment else comment

    @classmethod
    def _extract_definitions(cls, alist, level=None):
        """
        Since we couldn't be bothered to register models elsewhere
        our definitions need to be extracted from the parameters.
        We require an 'id' field for the schema to be correctly
        added to the definitions list.
        """

        def _extract_array_defs(source):
            # extract any definitions that are within arrays
            # this occurs recursively
            ret = []
            items = source.get('items')
            if items is not None and 'schema' in items:
                ret += cls._extract_definitions([items], level + 1)
            return ret

        # for tracking level of recursion
        if level is None:
            level = 0

        defs = list()
        if alist is not None:
            for item in alist:
                schema = item.get("schema")
                if schema is not None:
                    schema_id = schema.get("id")
                    if schema_id is not None:
                        defs.append(schema)
                        ref = {"$ref": "#/definitions/{}".format(schema_id)}

                        # only add the reference as a schema if we are in a response or
                        # a parameter i.e. at the top level
                        # directly ref if a definition is used within another definition
                        if level == 0:
                            item['schema'] = ref
                        else:
                            item.update(ref)
                            del item['schema']

                    # extract any definitions that are within properties
                    # this occurs recursively
                    properties = schema.get('properties')
                    if properties is not None:
                        defs += cls._extract_definitions(properties.values(), level + 1)

                    defs += _extract_array_defs(schema)

                defs += _extract_array_defs(item)

        return defs

    def save(self, path='', filename='swagger.json'):
        with open(os.path.join(path, filename), 'wb') as f:
            f.write(self.dump_schema())

    def dump_schema(self):
        return json.dumps(self.output, indent=2)
