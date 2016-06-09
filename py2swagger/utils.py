import imp
import importlib
import inspect
import six
import types
import yaml
from copy import deepcopy
from collections import OrderedDict

# Ability to load and dump yaml as OrderedDict
from yaml import resolver

from .config import SWAGGER_SETTINGS

_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_representer(dumper, data):
    return dumper.represent_dict(six.iteritems(data))


def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))


yaml.add_representer(OrderedDict, dict_representer)
yaml.add_constructor(_mapping_tag, dict_constructor)

ALLOWED = 'all'


class YAMLLoaderMixin(object):

    @staticmethod
    def yaml_load(data):
        try:
            return yaml.load(data)
        except (yaml.YAMLError, AttributeError):
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


def get_mro_list(instance, only_parents=True):
    mro = []
    if inspect.isclass(instance):
        mro = inspect.getmro(instance)
        if only_parents:
            mro = mro[1:]
    return mro


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


def _extract_class_path(path):
    module_path = None
    class_name = path

    if '.' in path:
        module_path, class_name = path.rsplit('.', 1)

    return module_path, class_name


def _load_class_obj(module_path, class_name, package=None):
    class_obj = None
    try:
        module = importlib.import_module(module_path, package)
        class_obj = getattr(module, class_name, None)
    except ImportError:
        pass

    return class_obj


def load_class(path):
    if path.startswith('.'):
        # is it relative path?
        # TODO: may be later
        raise ImportError('Relative class path is not supported {}'.format(path))

    module_path, class_name = _extract_class_path(path)
    if module_path is None:
        # is class located in current module?
        # TODO: may be later
        raise ImportError('Absolute module path is required {}'.format(path))

    class_obj = _load_class_obj(module_path, class_name)
    if class_obj is None:
        raise ImportError('Could not find {}'.format(path))

    return class_obj


def update_settings(settings, settings_part):
    for param_name, param_value in settings_part.items():
        if param_name in settings and isinstance(settings[param_name], dict):
            settings[param_name].update(param_value)
        elif param_name in settings and isinstance(settings[param_name], list):
            settings[param_name].extend(param_value)
        else:
            settings[param_name] = param_value

    return settings


def get_settings(local_config_file_path=None):
    swagger_settings = SWAGGER_SETTINGS.copy()
    plugin_settings = {}

    if local_config_file_path:
        custom_config = imp.load_source('config', local_config_file_path)
        swagger_settings.update(getattr(custom_config, 'SWAGGER_SETTINGS', dict()))
        plugin_settings.update(getattr(custom_config, 'PLUGIN_SETTINGS', dict()))

    return swagger_settings, plugin_settings
