# encoding: utf-8
from __future__ import absolute_import
import os
import sys
from distutils.version import StrictVersion

import django
from rest_framework import VERSION as REST_FRAMEWORK_VERSION

from .. import FIXTURES_PATH

sys.path.append(os.path.join(FIXTURES_PATH, 'drf_application'))

REST_FRAMEWORK_V3 = StrictVersion(REST_FRAMEWORK_VERSION) >= StrictVersion('3.0.0')
REST_FRAMEWORK_V35 = StrictVersion(REST_FRAMEWORK_VERSION) >= StrictVersion('3.5.0')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

test_runner = None
old_config = None

if hasattr(django, 'setup'):
    django.setup()

try:
    # for Django<1.10
    from django.conf.urls import patterns
except ImportError:
    # for Django>=1.10
    def patterns(*args):
        return list(filter(lambda x: x, args))


def setup():
    global test_runner
    global old_config

    try:
        # DjangoTestSuiteRunner was deprecated in django 1.8:
        # https://docs.djangoproject.com/en/1.8/internals/deprecation/#deprecation-removed-in-1-8
        from django.test.runner import DiscoverRunner as TestSuiteRunner
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner as TestSuiteRunner

    test_runner = TestSuiteRunner()
    test_runner.setup_test_environment()
    test_runner.setup_databases()


def teardown():
    # test_runner.teardown_databases(old_config)
    test_runner.teardown_test_environment()
