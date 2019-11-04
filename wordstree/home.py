from wordstree.db import get_db
from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app
from werkzeug.security import generate_password_hash

bp = Blueprint('root', __name__)


@bp.route('/home')
@bp.route('/')
def home():
    """ Handles requests to the root page """
    return render_template('home.html')


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


