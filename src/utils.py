import importlib
import inspect
import six
import types
import yaml

from copy import deepcopy
from collections import namedtuple

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # NOQA

# Ability to load and dump yaml as OrderedDict
from yaml import resolver

_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    return dumper.represent_dict(six.iteritems(data))


def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))


yaml.add_representer(OrderedDict, dict_representer)
yaml.add_constructor(_mapping_tag, dict_constructor)

unwrappage = namedtuple('unwrappage', ['closure', 'code'])

ALLOWED = 'all'


class YAMLLoaderMixin(object):

    @staticmethod
    def yaml_load(obj):
        try:
            return yaml.load(obj)
        except yaml.YAMLError:
            return None


def flatten(seq):
    l = []
    for elt in seq:
        t = type(elt)
        if t is tuple or t is list:
            for elt2 in flatten(elt):
                l.append(elt2)
        else:
            l.append(elt)
    return l


def clean_parameters(parameters, method=ALLOWED):
    # If formData and body parameters presents
    # and file in formData then remove body
    # else remove all formData parameters
    formdata_file = any(p['in'] == 'formData' and p.get('type', None) == 'file' for p in parameters)

    if formdata_file:
        parameters = [p for p in parameters if not p['in'] == 'body']
    else:
        parameters = [p for p in parameters if not p['in'] == 'formData']

    # Remove duplicates and check parameter method
    parameters_set = set()
    cleaned_parameters = []
    for parameter in parameters:
        name = parameter['name']
        if name in parameters_set:
            continue

        p = deepcopy(parameter)
        methods = p.pop('methods', [ALLOWED])

        if method in methods or ALLOWED in methods:
            cleaned_parameters.append(p)
            parameters_set.add(name)

    return cleaned_parameters


def closure_n_code(func):
    return unwrappage(
        six.get_function_closure(func),
        six.get_function_code(func))


def get_mro_list(instance, only_parents=True):
    mro = []
    if inspect.isclass(instance):
        mro = inspect.getmro(instance)
        if only_parents:
            mro = mro[1:]
    return mro


def get_closure_var(func, name=None):
    unwrap = closure_n_code(func)
    if name:
        index = unwrap.code.co_freevars.index(name)
        return unwrap.closure[index].cell_contents
    else:
        for closure_var in unwrap.closure:
            if isinstance(closure_var.cell_contents, types.FunctionType):
                return closure_var.cell_contents
        else:
            return None


def get_decorators(function):
    # If we have no func_closure, it means we are not wrapping any other functions.
    decorators = []

    try:
        func_closure = six.get_function_closure(function)
    except AttributeError:
        return decorators
    if not func_closure:
        return [function]
    # Otherwise, we want to collect all of the recursive results for every closure we have.
    for closure in func_closure:
        if isinstance(closure.cell_contents, types.FunctionType):
            decorators.extend(get_decorators(closure.cell_contents))
    return [function] + decorators


def multi_getattr(obj, attr, default=None):
    """
    Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.
    """
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default:
                return default
            else:
                raise
    return obj


def load_class(path, callback):
    """
    Dynamically load a class from a string
    """
    if not path or not callback or not hasattr(callback, '__module__'):
        return None

    package = None
    if '.' not in path:
        # within current module/file
        class_name = path
        module_path = callback.__module__
    else:
        # relative or fully qualified path import
        class_name = path.split('.')[-1]
        module_path = ".".join(path.split('.')[:-1])

        if path.startswith('.'):
            # relative lookup against current package
            # ..serializers.FooSerializer
            package = callback.__module__

    class_obj = None
    # Try to perform local or relative/fq import
    try:
        module = importlib.import_module(module_path, package=package)
        class_obj = getattr(module, class_name, None)
    except ImportError:
        pass

    # Class was not found, maybe it was imported to callback module?
    # from app.serializers import submodule
    # serializer: submodule.FooSerializer
    if class_obj is None:
        try:
            module = importlib.import_module(callback.__module__)
            class_obj = multi_getattr(module, path)
        except (ImportError, AttributeError):
            raise Exception("Could not find %s" % path)

    return class_obj
