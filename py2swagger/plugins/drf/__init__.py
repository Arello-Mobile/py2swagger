import os

from py2swagger.plugins import Py2SwaggerPlugin, Py2SwaggerPluginException


class DjangoPlugin(Py2SwaggerPlugin):

    help = 'Plugin for Django REST Framework applications'

    def set_parser_arguments(self, parser):
        parser.add_argument('django_settings', help='Path to django settings module')
        parser.add_argument('-f', '--filter', help='Filter urls that contains a pattern')

    def run(self, arguments, *args, **kwargs):
        try:
            os.environ.setdefault(
                'DJANGO_SETTINGS_MODULE', arguments.django_settings)
            import django
            if hasattr(django, 'setup'):
                django.setup()
        except ImportError:
            raise Py2SwaggerPluginException('Invalid django settings module')

        from .introspectors.api import ApiIntrospector
        from .urlparser import UrlParser

        # Patch Djago REST Framework, to make inspection process slightly easier
        from . import injection

        apis = UrlParser().get_apis(filter_path=arguments.filter)
        a = ApiIntrospector(apis)

        return a.inspect()
