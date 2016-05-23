import re

from .utils import OrderedDict, YAMLLoaderMixin


class YAMLDocstringParser(YAMLLoaderMixin):
    """
    YAML docstring parser
    """

    def __init__(self, docstring=''):
        self.doc = docstring or ''

        self.summary, self.description, self.schema = self._parse_docstring(self.doc)

    def _parse_docstring(self, docstring=''):
        """
        :param docstring:
        :return: (summary, description, schema)
        """
        summary, description, schema = None, None, dict()
        docstring = docstring.strip()

        if '---' in docstring:
            head, yml = re.split(r'\s*---+\s*\n', docstring)
            if yml:
                schema = self.yaml_load(yml) or dict()
        else:
            head = docstring

        if '\n' in head.strip():
            summary, description = map(lambda s: s.strip(), head.split('\n', 1))
        elif head:
            summary = head.strip()

        return summary, description, schema

    def get_description(self):
        """
        :return: Description found in docstring
        :rtype: str
        """
        return self.description

    def get_summary(self):
        """
        :return: Summary found in docstring
        :rtype: str
        """
        return self.summary

    def get_tags(self):
        """
        :return: Tags found in docstring
        :rtype: list
        """
        return self.schema.get('tags', list())

    def get_parameters(self):
        """
        :return: Parameters found in docstring
        :rtype: list
        """
        return self.schema.get('parameters', list())

    def get_responses(self):
        """
        :return: Responses found in docstring
        :rtype: dict
        """
        return self.schema.get('responses', dict())

    def get_serializer(self, request=False):
        """
        Get serializer found in docstring

        :param request: is request serializer?
        :return: Serializer path
        :rtype: str
        """
        serializer = None
        serializers = self.schema.get('serializers', None)
        serializer_type = 'request' if request else 'response'
        if serializers:
            raw = serializers.get(serializer_type, dict())
            serializer = raw.get('path', None)
        return serializer

    def get_serializers(self):
        """
        Get all serializers found in docstring

        :return: list of serializers path
        :rtype: list
        """
        serializers = []
        for key, value in self.schema.get('serializers', dict()).items():
            path = value.get('path', None)
            if path:
                serializers.append(path)
        return serializers

    def get_response_serializer(self):
        """
        Get response serializer found in docstring

        :return: Serializer path
        :rtype: str
        """
        return self.get_serializer()

    def get_request_serializer(self):
        """
        Get request serializer found in docstring

        :return: Serializer path
        :rtype: str
        """
        return self.get_serializer(request=True)

    def get_security(self):
        """
        :return: Parameters found in docstring
        :rtype: list
        """
        return self.schema.get('security', list())

    def get_security_definitions(self):
        """
        :return: Responses found in docstring
        :rtype: dict
        """
        return self.schema.get('securityDefinitions', dict())

    def update(self, docstring=''):
        """
        Update parser with another docstring
        :param docstring:
        """
        if docstring is None:
            docstring = ''
        summary, description, schema = self._parse_docstring(docstring)

        # update summary
        self.summary = summary or self.summary
        # update description
        self.description = description or self.description

        # update schema
        for k, v in schema.items():
            if k not in self.schema:
                self.schema[k] = v
            else:
                if isinstance(v, list):
                    self.schema[k].extend(v)
                elif isinstance(v, (dict, OrderedDict)):
                    self.schema[k].update(v)
