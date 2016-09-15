import os
import sys
from unittest import TestCase

from py2swagger.plugins.simple import SimplePlugin
from py2swagger.plugins import Py2SwaggerPluginException
from py2swagger.utils import get_settings

from .. import unordered, FIXTURES_PATH


class SimplePluginTestCase(TestCase):

    def test_plugin_settings(self):
        SimplePlugin().run(None, endpoints=[])

    def test_plugin_settings_missed(self):
        self.assertRaises(Py2SwaggerPluginException, SimplePlugin().run, [])


class BottleApplicationTestCase(TestCase):

    def setUp(self):
        sys.path.append(os.path.join(FIXTURES_PATH, 'bottle_application'))

    def tearDown(self):
        sys.path.remove(os.path.join(FIXTURES_PATH, 'bottle_application'))

    def test_bottle_application(self):
        _, plugin_settings = get_settings(os.path.join(FIXTURES_PATH, 'bottle_application', 'py2swagger.py'))
        expected_parts = {
            "paths": {
                "/hello": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Returns 'Hello, World!'",
                                "schema": {
                                    "type": "string"
                                }
                            }
                        },
                        "tags": [
                            "greetings",
                            "unrestricted"
                        ],
                        "summary": "Greeting users with 'Hello, World!'"
                    }
                },
                "/world": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Greetings was succesfully done",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string"
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Unauthorized"
                            }
                        },
                        "tags": [
                            "greetings",
                            "restricted"
                        ],
                        "security": [
                            {
                                "basic": []
                            }
                        ]
                    }
                }
            },
            'securityDefinitions': {}
        }

        swagger_part = SimplePlugin().run(None, endpoints=plugin_settings['endpoints'])
        self.assertDictEqual(expected_parts, unordered(swagger_part))


class FlaskApplicationTestCase(TestCase):
    def setUp(self):
        sys.path.append(os.path.join(FIXTURES_PATH, 'flask_application'))

    def tearDown(self):
        sys.path.remove(os.path.join(FIXTURES_PATH, 'flask_application'))

    def test_flask_application(self):
        _, plugin_settings = get_settings(os.path.join(FIXTURES_PATH, 'flask_application', 'py2swagger.py'))
        expected_parts = {
            "paths": {
                "/hello": {
                    "GET": {
                        "responses": {
                            "200": {
                                "schema": {
                                    "type": "string"
                                }
                            }
                        },
                        "tags": [
                            "greeting"
                        ],
                        "summary": "Greetings users with 'Hello, World!'"
                    }
                }
            },
            "securityDefinitions": {}
        }

        swagger_part = SimplePlugin().run(None, endpoints=plugin_settings['endpoints'])
        self.assertDictEqual(expected_parts, unordered(swagger_part))
