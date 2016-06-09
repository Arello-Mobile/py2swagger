from flask import Flask


app = Flask(__name__)


@app.route('/hello')
def hello_world():
    """
    Greetings users with 'Hello, World!'
    ---
    tags:
    - greeting
    responses:
      200:
        schema:
          type: string
    """
    return 'Hello, World!'
