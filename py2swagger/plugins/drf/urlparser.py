from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.utils import six
from importlib import import_module

from rest_framework.views import APIView


class UrlParser(object):

    def get_apis(self, url_patterns=None, urlconf=None, filter_path=None, exclude_namespaces=None):
        """
        Returns all the DRF APIViews found in the project URLs
        patterns -- supply list of patterns (optional)
        exclude_namespaces -- list of namespaces to ignore (optional)
        """

        if not url_patterns and urlconf:
            if isinstance(urlconf, six.string_types):
                urls = import_module(urlconf)
            else:
                urls = urlconf
            url_patterns = urls.urlpatterns
        elif not url_patterns and not urlconf:
            urls = import_module(settings.ROOT_URLCONF)
            url_patterns = urls.urlpatterns

        formatted_apis = self.format_api_patterns(
            url_patterns,
            filter_path=filter_path,
            exclude_namespaces=exclude_namespaces,
        )

        return formatted_apis

    def format_api_patterns(self, url_patterns, prefix='', filter_path=None, exclude_namespaces=None):
        """
        Uses recursion to format url tree.
        patterns -- urlpatterns list
        prefix -- (optional) Prefix for URL pattern
        """
        url_patterns_list = []

        for pattern in url_patterns:

            if hasattr(pattern, 'url_patterns'):
                if exclude_namespaces and pattern.namespace in exclude_namespaces:
                    continue
                pref = prefix + pattern.regex.pattern
                url_patterns_list.extend(self.format_api_patterns(
                    pattern.url_patterns,
                    pref,
                    filter_path=filter_path,
                    exclude_namespaces=exclude_namespaces,
                ))
            else:
                endpoint_data = self.gather_endpoint_data(pattern, prefix, filter_path=filter_path)

                if endpoint_data:
                    url_patterns_list.append(endpoint_data)

        if filter_path:
            url_patterns_list = [api for api in url_patterns_list if filter_path in api['path'].strip('/')]

        return url_patterns_list

    def gather_endpoint_data(self, pattern, prefix='', filter_path=None):
        """
        Creates a dictionary for matched API urls

        pattern -- the pattern to parse
        prefix -- the API path prefix (used by recursion)
        """
        callback = self.filter_api_view_callbacks(pattern)

        if callback:
            path = simplify_regex(prefix + pattern.regex.pattern)

            if self.is_router_api_root(callback) or filter_path and filter_path not in path:
                return

            path = path.replace('<', '{').replace('>', '}')

            # These additional RegexURLPatterns paths are duplicated by DRF and not needed.
            if '.{format}' in path:
                return

            return {
                'path': path,
                'pattern': pattern,
                'callback': callback,
            }

    @classmethod
    def filter_api_view_callbacks(cls, url_pattern):
        if not hasattr(url_pattern, 'callback'):
            return

        if hasattr(url_pattern.callback, 'cls') and issubclass(url_pattern.callback.cls, APIView):
            return url_pattern.callback.cls

    @classmethod
    def is_router_api_root(cls, callback):
        """
        If URL's callback is rest_framework.routers.APIRoot returns True
        """
        if callback.__module__ == 'rest_framework.routers':
            return True

