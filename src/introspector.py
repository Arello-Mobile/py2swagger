import inspect

from .utils import get_mro_list, get_decorators, OrderedDict
from .yamlparser import YAMLDocstringParser


class BaseDocstringIntrospector(object):
    """
    Base docstring introspector collects yaml docstrings from:
    - instance docstring
    - instance decorators docstrings
    - instance mro docstrings
    """

    def __init__(self, instance):
        """
        :param instance: class or function
        """
        self.instance = instance
        self.parser = self._create_parser()
        self.mro_parser = self._create_mro_parser()
        self.decorators_parser = self._create_decorators_parser()

        self.parsers = [
            self.mro_parser,
            self.decorators_parser,
            self.parser
        ]

    @staticmethod
    def _get_doc(instance):
        """
        Get instance docstring

        :param instance: class or object
        :return: instance docstring
        :rtype: str
        """
        return inspect.getdoc(instance)

    def _create_mro_parser(self):
        """
        Creates instance mro yaml parser

        :return: yaml parser
        :rtype: YAMLDocstringParser
        """
        parent_classes = get_mro_list(self.instance)[::-1]
        return self._create_parser(parent_classes)

    def _create_decorators_parser(self):
        """
        Creates instance decorators yaml parser

        :return: yaml parser
        :rtype: YAMLDocstringParser
        """
        decorators = get_decorators(self.instance)[1:] if self.instance else []
        return self._create_parser(decorators)

    def _create_parser(self, instances=None):
        """
        Creates yaml parser from instance(s)

        :param list object instances:
        :return: yaml parser
        :rtype: YAMLDocstringParser
        """
        instances = instances if instances is not None else [self.instance]
        parser = YAMLDocstringParser()
        for instance in instances:
            doc = self._get_doc(instance)
            parser.update(doc)
        return parser

    @property
    def parameters(self):
        """
        Collects pararameters from all parsers

        :return: parameters
        :rtype: list
        """
        parameters = []
        for parser in self.parsers:
            parameters.extend(parser.get_parameters())
        return parameters

    @property
    def responses(self):
        """
        Collects responses from all parsers

        :return: responses
        :rtype: OrderedDict
        """
        responses = OrderedDict()
        for parser in self.parsers:
            responses.update(parser.get_responses())
        return responses
