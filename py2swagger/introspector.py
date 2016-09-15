import inspect

from .utils import get_mro_list, get_decorators, OrderedDict
from .yamlparser import YAMLDocstringParser


class BaseDocstringIntrospector(object):
    """
    Base docstring introspector collects yaml docstrings from:
    - instance docstring
    - instance decorators docstrings
    - instance base class docstrings
    """

    def __init__(self, instance):
        """
        :param instance: class or function
        """
        self._instance = instance

        self._parser = self._create_parser(instance)
        self._inheritances_parser = self._create_parser(self._get_inheritances(instance))
        self._decorators_parser = self._create_parser(self._get_decorators(instance))

        self._parsers = (
            self._inheritances_parser,
            self._decorators_parser,
            self._parser,
        )

    @property
    def parser(self):
        """
        Returns current object parser
        """
        return self._parsers[-1]

    @property
    def parsers(self):
        """
        Returns list of parsers
        """
        return self._parsers

    @staticmethod
    def _get_doc(instance):
        """
        Get instance docstring

        :param instance: class or object
        :return: instance docstring
        :rtype: str
        """
        return inspect.getdoc(instance)

    @staticmethod
    def _get_inheritances(instance):
        """
        Returns list of base objects for instance

        :param instance: class or object
        :return: list of objects
        :rtype: list
        """
        return list(get_mro_list(instance)[::-1])

    @staticmethod
    def _get_decorators(instance):
        """
        Returns list of decorators for instance

        :param instance: class or object
        :return: list of objects
        :rtype: list
        """
        return get_decorators(instance)[1:]

    def _create_parser(self, instances):
        """
        Creates yaml parser from instance(s)

        :param list object instances:
        :return: yaml parser
        :rtype: YAMLDocstringParser
        """
        if not isinstance(instances, (list, tuple)):
            instances = [instances]

        parser = YAMLDocstringParser()
        for instance in instances:
            doc = self._get_doc(instance)
            parser.update(doc)
        return parser

    @property
    def tags(self):
        """
        Collects tags from all parsers

        :return: parameters
        :rtype: list
        """
        tags = []
        for parser in self._parsers:
            tags.extend(parser.get_tags())
        return tags

    @property
    def parameters(self):
        """
        Collects parameters from all parsers

        :return: parameters
        :rtype: list
        """
        parameters = []
        for parser in self._parsers:
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
        for parser in self._parsers:
            responses.update(parser.get_responses())
        return responses

    @property
    def security(self):
        """
        Collects security from all parsers
    
        :return: security
        :rtype: list
        """
        security = []
        for parser in self._parsers:
            security.extend(parser.get_security())
        return security
        
    @property
    def security_definitions(self):
        """
        Collects securityDefinitions from all parsers
    
        :return: security_definitions
        :rtype: OrderedDict
        """
        security_definitions = OrderedDict()
        for parser in self._parsers:
            security_definitions.update(parser.get_security_definitions())
        return security_definitions
