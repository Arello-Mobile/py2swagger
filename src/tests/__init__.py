# encoding: utf-8
from __future__ import absolute_import

import os
import django

test_runner = None
old_config = None

os.environ['DJANGO_SETTINGS_MODULE'] = 'testapp.settings'

if hasattr(django, 'setup'):
    django.setup()


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
