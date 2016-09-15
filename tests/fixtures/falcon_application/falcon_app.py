import falcon


class TestResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ('\nTwo things awe me most, the starry sky '
                     'above me and the moral law within me.\n'
                     '\n'
                     '    ~ Immanuel Kant\n\n')


class TestResourceWithParemeter:
    def on_get(self, req, resp, id):
        """
        Handles GET requests for another test
        ---
        tags:
        - test
        responses:
          200:
            schema:
              type: string
        security:
          api_key: []
        securityDefinitions:
          api_key:
            type: apiKey
            in: Header
            name: Authorization
        """
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = '\nHello world with {}\n\n'.format(id)

app = falcon.API()
test = TestResource()
test_param = TestResourceWithParemeter()
app.add_route('/test2/{id}', test_param)
app.add_route('/test', test)
