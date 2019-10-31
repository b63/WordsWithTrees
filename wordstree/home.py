from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash

bp = Blueprint('root', __name__)


@bp.route('/')
def home():
    """ Handles requests to the root page """
    return render_template('home.html')


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def root():
    """ Handles requests to the root page. """
    return render_template('signup.html')


@app.route('/home')
def home():
    """ Handles requests to the root page. """
    return render_template('home.html')


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/register', methods=['POST'])
def register_form():
    """ Register user with a form. """

    # ensure name was submitted
    if not request.form.get("name"):
        flash("You must provide a name")
        return redirect(url_for('register_form'))

    # ensure username was submitted
    if not request.form.get("username"):
        flash("You must provide a username")
        return redirect(url_for('register_form'))

    # ensure password was submitted
    if not request.form.get("password"):
        flash("You must provide a password")
        return redirect(url_for('register_form'))

    # ensure password confirmation was submitted
    if not request.form.get("password-confirm"):
        flash("You must provide a password confirmation")
        return redirect(url_for('register_form'))

    # ensure password and confirmation match
    if request.form.get("password") != request.form.get("password-confirm"):
        flash("Your passwords must match")
        return redirect(url_for('register_form'))

    # hash password to not store the actual password
    password = request.form.get("password")
    hash_password = generate_password_hash(password)
    db = get_db()

    # username must be unique
    try:
        db.execute("INSERT INTO users (name, username, hash_password) VALUES (?, ?, ?)",
                   [request.form.get("name"), request.form.get("username"), hash_password])
    except sqlite3.IntegrityError:
        # pick another username
        flash("Your username has been used. Pick another username")
        return redirect(url_for('register_form'))

    # store their id in session to log them in automatically
    db.commit()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET'])
def register_page():
    """ Redirect to register form """
    return render_template("signup.html")





