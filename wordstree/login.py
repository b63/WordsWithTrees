from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import check_password_hash

bp = Blueprint('login', __name__)


@bp.route('/login', methods=['POST'])
def login_form():
    """ Login user with a form. """

    # ensure username was submitted
    if not request.form.get("username"):
        flash("You must provide a username")
        return redirect(url_for('login.login_page'))

    # ensure password was submitted
    if not request.form.get("password"):
        flash("You must provide a password")
        return redirect(url_for('login.login_page'))

    # query database for username
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
    user_data = cur.fetchone()

    # ensure username exists and password is correct
    if len(user_data) != 1 or not check_password_hash(user_data[0]["hash_password"], request.form.get("password")):
        flash("Invalid username and/or password")
        return redirect(url_for('login.login_page'))

    # remember which user has logged in
    session["user_id"] = user_data[0]["id"]

    # redirect user to home page
    return redirect(url_for("root.home"))


@bp.route('/login', methods=['GET'])
def login_page():
    """ Redirect user to login form. """
    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login_page"))
