from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import check_password_hash

bp = Blueprint('login', __name__)


@bp.route('/login', methods=['POST'])
def login_as_post():
    """ Login user with a form. """

    session.clear()

    # query database for username
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE username = (?)", [request.form.get("username")])
    user_data = cur.fetchone()

    # ensure username exists and password is correct
    if user_data is None or not check_password_hash(user_data["hash_password"], request.form.get("password")):
        flash("Invalid username and/or password.")
        return render_template("login.html")

    # remember which user has logged in
    session["user_id"] = user_data["id"]

    # insert login successful notification
    db.execute("INSERT INTO notifications (receiver_id, entity_id) VALUES (?, ?)", [user_data["id"], 1])
    db.commit()

    # redirect user to marketplace with user's inventory shown
    return redirect(url_for("view_inventory.view_inventory"))


@bp.route('/login', methods=['GET'])
def login_as_get():
    """ Redirect user to login form. """
    return render_template("login.html")

#
@bp.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("root.home"))
