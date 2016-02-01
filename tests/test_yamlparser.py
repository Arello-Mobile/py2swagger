from unittest import TestCase
from py2swagger.yamlparser import YAMLDocstringParser


class YAMLDocstringParserTestCase(TestCase):
    def setUp(self):
        self.docstring = """
        Summary
        Multiline Description
        Long Long Description
        ---
        tags:
        - tag1
        - tag2
        parameters:
        - in: query
          name: param1
          type: integer
        - in: query
          name: param2
          type: string
        responses:
          200:
            description: Description
            schema:
              type: object
              properties:
                prop1:
                  type: string
                prop2:
                  type: integer
        serializers:
          request:
            path: some.path.to.RequestSerializer
          response:
            path: some.path.to.ResponseSerializer
        """

        self.parser = YAMLDocstringParser(self.docstring)

    def test_empty_docstring(self):
        parser = YAMLDocstringParser()

        self.assertEqual(dict(), parser.schema)
        self.assertEquals(None, parser.get_summary())
        self.assertEquals(None, parser.get_description())
        self.assertEqual([], parser.get_tags())
        self.assertEqual([], parser.get_parameters())
        self.assertEqual(dict(), parser.get_responses())
        self.assertEqual(None, parser.get_response_serializer())
        self.assertEqual(None, parser.get_request_serializer())

    def test_invalid_yaml(self):

        docstring = """
        ---
        invalid:
            - yaml
        - here:here
            - yaml
        """
        parser = YAMLDocstringParser(docstring)

        self.assertEqual(dict(), parser.schema)

    def test_summary(self):
        docstring = """
        Summary
        ---
        key: value
        """

        parser = YAMLDocstringParser(docstring)
        self.assertEqual('Summary', parser.get_summary())

        docstring = """
            Summary
            Description
            ---
            key: value
            """
        parser = YAMLDocstringParser(docstring)
        self.assertEqual('Summary', parser.get_summary())

        docstring = """
        ---
        key: value
        """

        parser = YAMLDocstringParser(docstring)
        self.assertFalse(parser.get_summary())

        self.assertEquals('Summary', self.parser.get_summary())

    def test_description(self):
        docstring = """
            Summary
            ---
            key: value
            """

        parser = YAMLDocstringParser(docstring)
        self.assertIsNone(parser.get_description())

        docstring = """
                Summary
                Description
                ---
                key: value
                """
        parser = YAMLDocstringParser(docstring)
        self.assertEqual('Description', parser.get_description())

        docstring = """
            ---
            key: value
            """

        parser = YAMLDocstringParser(docstring)
        self.assertIsNone(parser.get_description())

        self.assertIn('Description', self.parser.get_description())
        self.assertIn('Long', self.parser.get_description())
        self.assertIn('\n', self.parser.get_description())

    def test_tags(self):
        docstring = """
        ---
        tags:
        - tag1
        - tag2
        """

        parser = YAMLDocstringParser(docstring)
        tags = parser.get_tags()

        self.assertEquals(2, len(tags))
        self.assertIn('tag1', tags)
        self.assertIn('tag2', tags)

        docstring = """
        ---
        key: value
        """

        parser = YAMLDocstringParser(docstring)
        tags = parser.get_tags()
        self.assertEqual(list, type(tags))
        self.assertEquals(0, len(tags))

        tags = self.parser.get_tags()
        self.assertEquals(2, len(tags))
        self.assertIn('tag1', tags)
        self.assertIn('tag2', tags)

    def test_parameters(self):
        docstring = """
        ---
        parameters:
        - in: query
          name: p1
          type: integer
        - in: path
          name: p2
          type: string
        """

        parser = YAMLDocstringParser(docstring)
        parameters = parser.get_parameters()

        self.assertEquals(2, len(parameters))
        self.assertEqual('p1', parameters[0]['name'])
        self.assertEqual('p2', parameters[1]['name'])

        parameters = self.parser.get_parameters()
        self.assertEquals(2, len(parameters))
        self.assertEqual('param1', parameters[0]['name'])
        self.assertEqual('param2', parameters[1]['name'])

    def test_responses(self):
        docstring = """
        ---
        responses:
          200:
            description: Good Response
          403:
            description: Bad Response
        """

        parser = YAMLDocstringParser(docstring)
        responses = parser.get_responses()

        self.assertIn(200, responses.keys())
        self.assertIn(403, responses.keys())

        responses = self.parser.get_responses()

        self.assertIn(200, responses.keys())

    def test_response_serializer(self):
        response_serializer = self.parser.get_response_serializer()

        self.assertEqual('some.path.to.ResponseSerializer', response_serializer)

    def test_request_serializer(self):
        response_serializer = self.parser.get_request_serializer()
        self.assertEqual('some.path.to.RequestSerializer', response_serializer)

    def test_get_serializers(self):
        serializers = self.parser.get_serializers()
        self.assertEqual(2, len(serializers))
        self.assertIn('some.path.to.RequestSerializer', serializers)
        self.assertIn('some.path.to.ResponseSerializer', serializers)

    def test_update(self):
        parser = YAMLDocstringParser(self.docstring)

        docstring = """
        New summary
        New description
        ---
        tags:
        - tag3
        parameters:
        - in: query
          name: param3
          type: string
        responses:
          200:
            description: Updated response
          400:
            description: New response
        serializers:
          request:
            path: path.to.new.RequestSerializer
        """

        parser.update(docstring)

        # Check tags updated
        tags = parser.get_tags()
        self.assertEqual(3, len(tags))
        self.assertIn('tag3', tags)

        # Check parameters appended
        parameters = parser.get_parameters()
        self.assertEqual(3, len(parameters))
        self.assertEqual('param3', parameters[2]['name'])

        # Check responses updated
        responses = parser.get_responses()
        self.assertEqual(2, len(responses.keys()))
        self.assertIn(400, responses.keys())
        self.assertEqual('Updated response', responses[200]['description'])

        # Check serializer updated
        request_serializer = parser.get_request_serializer()
        self.assertEqual('path.to.new.RequestSerializer', request_serializer)
