from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session
from werkzeug.security import generate_password_hash

bp = Blueprint('root', __name__)


@bp.route('/', methods=['GET', 'POST'])
def home():
    """ Handles requests to the root page """
    if request.method == 'POST':
        if 'sign up' in request.form:
            return redirect(url_for("signup.signup_as_get"))
        elif 'log in' in request.form:
            return redirect(url_for("login.login_page"))

    return render_template('index.html')


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


