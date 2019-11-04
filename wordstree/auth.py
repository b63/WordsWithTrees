from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import generate_password_hash

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register_form():
    """ Register user with a form. """

    # ensure name was submitted
    if not request.form.get("name"):
        flash("You must provide a name")
        return redirect(url_for('auth.register_form'))

    # ensure username was submitted
    if not request.form.get("username"):
        flash("You must provide a username")
        return redirect(url_for('auth.register_form'))

    # ensure password was submitted
    if not request.form.get("password"):
        flash("You must provide a password")
        return redirect(url_for('auth.register_form'))

    # ensure password confirmation was submitted
    if not request.form.get("password-confirm"):
        flash("You must provide a password confirmation")
        return redirect(url_for('auth.register_form'))

    # ensure password and confirmation match
    if request.form.get("password") != request.form.get("password-confirm"):
        flash("Your passwords must match")
        return redirect(url_for('auth.register_form'))

    # ensure password meets policy
    # https://stackoverflow.com/questions/17140408/if-statement-to-check-whether-a-string-has-a-capital-letter-a-lower-case-letter/17140466
    rules = [lambda s: any(x.isupper() for x in request.form.get("password")),  # must have at least one uppercase
             lambda s: any(x.islower() for x in request.form.get("password")),  # must have at least one lowercase
             lambda s: any(x.isdigit() for x in request.form.get("password")),  # must have at least one digit
             lambda s: len(s) >= 7  # must be at least 7 characters
             ]

    if not all(rule(request.form.get("password")) for rule in rules):
        flash("Password must have at least 7 characters, including at least one uppercase, one lowercase, and one digit")
        return redirect(url_for('auth.register_form'))

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
        return redirect(url_for('auth.register_form'))

    db.commit()
    # store their id in session to log them in automatically
    cur = db.execute("SELECT id FROM users WHERE username=(?)",
                         [request.form.get("username")])
    user_id = cur.fetchone()
    
    session['user_id'] = user_id['id']

    return redirect(url_for('root.home'))


@bp.route('/register', methods=['GET'])
def register_page():
    """ Redirect to register form """
    return render_template("signup.html")
