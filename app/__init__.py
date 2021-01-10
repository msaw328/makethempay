# app module - create the base Flask app and mount routes

import os
from flask import Flask
from flask_jsglue import JSGlue

def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    jsglue = JSGlue(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # if running development load dev config, else load from instance file
    if 'ENV' in app.config and app.config['ENV'] == 'development':
        from .dev import config as dev_config

        app.config.from_mapping(dev_config)
    else:
        app.config.from_pyfile('prod.cfg')

    # open db and stuff
    from . import db
    db.init_app(app)

    # expand context
    from .utils.login import context_processor as login_context_processor
    app.context_processor(login_context_processor)

    # routes
    from .controllers import auth
    app.register_blueprint(auth.router, url_prefix='/auth')

    if 'ENV' in app.config and app.config['ENV'] == 'development':
        print('ENDPOINTS:')
        print(app.url_map)

    return app
