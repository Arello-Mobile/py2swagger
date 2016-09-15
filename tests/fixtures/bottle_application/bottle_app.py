from bottle import Bottle, auth_basic

app = Bottle()


def auth(user, password):
    return user == 'basic' and password == 'auth'


@app.route('/hello')
def hello():
    """
    Greeting users with 'Hello, World!'
    ---
    tags:
    - greetings
    - unrestricted
    responses:
      200:
        description: Returns 'Hello, World!'
        schema:
          type: string
    """
    return 'Hello, World!'


@app.route('/world')
@auth_basic(auth)
def world():
    """
    Greeting users with 'Hi!'
    ---
    tags:
    - greetings
    - restricted
    security:
    - basic: []
    responses:
      200:
        description: Greetings was succesfully done
        schema:
          type: object
          properties:
            status:
              type: string
      401:
        description: Unauthorized
    """
    return {'message': 'Hi!'}


if __name__ == '__main__':
    from bottle import run
    run(app, host='127.0.0.1', port=8000)
