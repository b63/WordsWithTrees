import click
import os

from sqlite3 import dbapi2 as sqlite3
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(initdb_command)


def init_db():
    """Initializes the database."""
    db = get_db()
    dir = os.path.join(current_app.root_path, 'schemas')
    test_dir = os.path.join(current_app.root_path, '../tests/schemas')

    def run_schemas(_dir):
        # sort in case some need to run before others
        files = sorted(list(
            filter(
                lambda p: p.endswith('.sql') and os.path.isfile(os.path.join(_dir, p)),
                os.listdir(_dir)
            )
        ))

        click.echo('Reading schemas from {} ...'.format(_dir))
        for file in files:
            click.echo('    reading {}'.format(file))
            with open(os.path.join(_dir, file), mode='r') as f:
                db.cursor().executescript(f.read())

    run_schemas(dir)
    if current_app.config.get('TESTING', False) and os.path.exists(test_dir):
        run_schemas(test_dir)


@click.command('initdb')
@with_appcontext
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        #del g['sqlite_db']
