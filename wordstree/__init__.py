import os
from flask import Flask


# application factory
def create_app(test_config=None):
    # create our little application :)
    app = Flask(__name__)

    # Load default config and override config from an environment variable
    app.config.from_mapping(
        DATABASE=os.path.join(app.root_path, 'wwt.db'),
        DEBUG=True,
        SECRET_KEY='development key',
    )
    app.config.from_envvar('FLASKR_SETTINGS', silent=True)
    if test_config:
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)

    from . import home
    app.register_blueprint(home.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import view_inventory
    app.register_blueprint(view_inventory.bp)

    return app
