def test_method_callback():
    """
    Test Method
    ---
    tags:
    - test
    security:
    - test_token: []
    securityDefinitions:
      test_token:
        type: apiKey
        name: Auth-Token
        in: header
    responses:
      200:
        schema:
          type: string
    """
    pass
