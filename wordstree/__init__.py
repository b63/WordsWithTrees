import os
from flask import Flask

DATABASE_FILE = 'wwt.db'


# application factory
def create_app(test_config=None):
    # create our little application :)
    app = Flask(__name__)

    # Load default config and override config from an environment variable
    app.config.from_mapping(
        DATABASE=os.path.join(app.root_path, DATABASE_FILE),
        DEBUG=True,
        SECRET_KEY='development key',
    )
    app.config.from_envvar('FLASKR_SETTINGS', silent=True)
    if test_config:
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)

    from .graphics import cli as graphics_cli
    graphics_cli.init_app(app)

    from . import home
    app.register_blueprint(home.bp)

    from . import login
    app.register_blueprint(login.bp)

    from . import signup
    app.register_blueprint(signup.bp)

    from . import view_inventory
    app.register_blueprint(view_inventory.bp)

    from . import buy_branches
    app.register_blueprint(buy_branches.bp)

    from . import sell_branches
    app.register_blueprint(sell_branches.bp)

    return app
