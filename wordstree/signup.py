from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import generate_password_hash

bp = Blueprint('signup', __name__)


@bp.route('/signup', methods=['POST'])
def signup_as_post():
    """ Register user with a form. """

    # ensure password and confirmation match
    if request.form.get("password") != request.form.get("password-confirm"):
        flash("Your passwords must match.")
        return render_template("signup.html")

    # ensure password meets policy
    # https://stackoverflow.com/questions/17140408/if-statement-to-check-whether-a-string-has-a-capital-letter-a-lower-case-letter/17140466
    rules = [lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
             lambda s: any(x.islower() for x in s),  # must have at least one lowercase
             lambda s: any(x.isdigit() for x in s),  # must have at least one digit
             lambda s: len(s) >= 7  # must be at least 7 characters
             ]

    if not all(rule(request.form.get("password")) for rule in rules):
        flash("Password must have at least 7 characters, including at least one uppercase, one lowercase, and one digit.")
        return render_template("signup.html")

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
        return render_template("signup.html")

    db.commit()
    # store their id in session to log them in automatically
    cur = db.execute("SELECT * FROM users WHERE username=(?)",
                     [request.form.get("username")])
    user_data = cur.fetchone()

    # automatically log in user and redirect to user's marketplace
    session['user_id'] = user_data['id']

    # insert signup and login succesful notification
    db.execute("INSERT INTO notifications (receiver_id, entity_id) VALUES (?, ?)", [user_data["id"], 2])
    db.commit()

    return redirect(url_for("view_inventory.view_inventory"))


@bp.route('/signup', methods=['GET'])
def signup_as_get():
    """ Redirect to register form """
    return render_template("signup.html")
