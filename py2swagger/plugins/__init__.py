from yapsy.IPlugin import IPlugin


class Py2SwaggerPluginException(Exception):
    pass


class Py2SwaggerPlugin(IPlugin):
    """ Interface for py2swagger plugins """

    #: help description
    summary = ''
    description = ''

    def set_parser_arguments(self, parser):
        """ Set arguments for command line parser

        :param argparse.ArgumentParser parser:
        """
        pass

    def run(self, arguments, *args, **kwargs):
        """ Run plugin logic

        :param argparse.Namespace arguments:
        :return: part of swagger object. This part contains "paths", "definitions" and "securityDefinitions"
        :rtype: dict
        """
        raise NotImplementedError()
