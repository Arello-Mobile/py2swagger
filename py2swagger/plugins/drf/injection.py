# Injection patches

from rest_framework.viewsets import ViewSetMixin
from django.utils.decorators import classonlymethod


def viewset_as_view_decorator(f):
    """
    ViewSetMixin.as_view is dynamically generates view function.
    It makes difficult to retrieves information about mapping: real_callback - http_method.
    This decorator make it slightly easy. It adds 'actions' as function parameter. This parameter
    contains information about mapping: real_callback - http_method.
    """
    f = f.__func__

    def _wrapped_as_view(cls, actions=None, **initkwargs):
        view_f = f(cls, actions, **initkwargs)
        view_f.actions = actions
        return view_f

    return classonlymethod(_wrapped_as_view)


ViewSetMixin.as_view = viewset_as_view_decorator(ViewSetMixin.as_view)
