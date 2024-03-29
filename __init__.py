import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    if os.getenv('FLASK_ENV') == 'development':
        url_path = '/develop'
    else:
        url_path = '/toolkit'
    app = Flask(__name__, instance_relative_config=True,static_url_path=url_path+'/static')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import toolkit
    app.register_blueprint(toolkit.bp)

    app.add_url_rule('/',endpoint='toolkit.index')

    return app
